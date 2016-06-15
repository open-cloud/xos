import threading
from cgi import escape as html_escape

from core.models import *
from core.models import Site
from django import forms
from django.contrib import admin, messages
from django.contrib.admin.widgets import (AdminTextareaWidget,
                                          FilteredSelectMultiple)
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import (AdminPasswordChangeForm,
                                       ReadOnlyPasswordHashField)
from django.contrib.auth.models import Group
from django.contrib.auth.signals import user_logged_in
from django.contrib.contenttypes import generic
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.urlresolvers import NoReverseMatch, resolve, reverse
from django.forms.utils import flatatt, to_current_timezone
from django.utils import timezone
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.html import conditional_escape, format_html
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from openstack.manager import OpenStackManager
from suit.widgets import LinkedSelect

# thread locals necessary to work around a django-suit issue
_thread_locals = threading.local()

ICON_URLS = {"success": "/static/admin/img/icon_success.gif",
             "clock": "/static/admin/img/icon_clock.gif",
             "error": "/static/admin/img/icon_error.gif"}


def backend_icon(obj):
    (icon, tooltip) = obj.get_backend_icon()

    icon_url = ICON_URLS.get(icon, "unknown")

    (exponent, last_success, last_failure, failures) = obj.get_backend_details()

    # FIXME: Need to clean this up by separating Javascript from Python
    if (obj.pk):
        script = """
        <script type="text/javascript">$(document).ready(function () {$("#show_details_%d").click(function () {$("#status%d").dialog({modal: true, height: 200, width: 200 });});});</script>
        """ % (obj.pk, obj.pk)

        div = """
        <div style="display:none;" id="status%d" title="Details">
                <p>Backoff Exponent: %r</p>
                <p>Last Success: %r</p>
                <p>Failures: %r</p>
                <p>Last Failure: %r</p>
                    </div>
        """ % (obj.pk, exponent, last_success, failures, last_failure)
        a = '<a id="show_details_%d" href="#">' % obj.pk
        astop = '</a>'
    else:
        div = ''
        script = ''
        a = ''
        astop = ''

    if tooltip:
        return '%s %s <span style="min-width:16px;" title="%s">%s<img src="%s">%s</span>' % (script, div, tooltip, a,  icon_url, astop)
    else:
        return '<span style="min-width:16px;"><img src="%s"></span>' % icon_url


def backend_text(obj):
    (icon, tooltip) = obj.get_backend_icon()
    icon_url = ICON_URLS.get(icon, "unknown")

    return '<img src="%s"> %s' % (icon_url, tooltip)


class UploadTextareaWidget(AdminTextareaWidget):

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        return format_html('<input type="file" style="width: 0; height: 0" id="btn_upload_%s" onChange="uploadTextarea(event,\'%s\');">'
                           '<button onClick="$(\'#btn_upload_%s\').click(); return false;">Upload</button>'
                           '<br><textarea{0}>\r\n{1}</textarea>' % (
                               attrs["id"], attrs["id"], attrs["id"]),
                           flatatt(final_attrs),
                           force_text(value))


class SliderWidget(forms.HiddenInput):

    def render(self, name, value,  attrs=None):
        if value is None:
            value = '0'
        final_attrs = self.build_attrs(attrs, name=name)
        attrs = attrs or attrs[:]
        attrs["name"] = name
        attrs["value"] = value
        html = """<div style="width:640px"><span id="%(id)s_label">%(value)s</span><div id="%(id)s_slider" style="float:right;width:610px;margin-top:5px"></div></div>
                              <script>
                                  $(function() {
                                      $("#%(id)s_slider").slider({
                                         value: %(value)s,
                                         slide: function(event, ui) { $("#%(id)s").val( ui.value ); $("#%(id)s_label").html(ui.value); },
                                         });
                                  });
                              </script>
                              <input type="hidden" id="%(id)s" name="%(name)s" value="%(value)s"></input>
                           """ % attrs
        html = html.replace("{", "{{").replace("}", "}}")
        return format_html(html,
                           flatatt(final_attrs),
                           force_text(value))


class PlainTextWidget(forms.HiddenInput):
    input_type = 'hidden'

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        return mark_safe(str(value) + super(PlainTextWidget, self).render(name, value, attrs))


class XOSAdminMixin(object):
    # call save_by_user and delete_by_user instead of save and delete

    def has_add_permission(self, request, obj=None):
        return (not self.__user_is_readonly(request))

    def has_delete_permission(self, request, obj=None):
        return (not self.__user_is_readonly(request))

    def save_model(self, request, obj, form, change):
        if self.__user_is_readonly(request):
            # this 'if' might be redundant if save_by_user is implemented right
            raise PermissionDenied

        # reset exponential backoff
        if hasattr(obj, "backend_register"):
            obj.backend_register = "{}"

        obj.caller = request.user
        # update openstack connection to use this site/tenant
        obj.save_by_user(request.user)

    def delete_model(self, request, obj):
        obj.delete_by_user(request.user)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.caller = request.user
            instance.save_by_user(request.user)

        # BUG in django 1.7? Objects are not deleted by formset.save if
        # commit is False. So let's delete them ourselves.
        #
        # code from forms/models.py save_existing_objects()
        try:
            forms_to_delete = formset.deleted_forms
        except AttributeError:
            forms_to_delete = []
        if formset.initial_forms:
            for form in formset.initial_forms:
                obj = form.instance
                if form in forms_to_delete:
                    if obj.pk is None:
                        continue
                    formset.deleted_objects.append(obj)
                    obj.delete()

        formset.save_m2m()

    def get_actions(self, request):
        actions = super(XOSAdminMixin, self).get_actions(request)

        if self.__user_is_readonly(request):
            if 'delete_selected' in actions:
                del actions['delete_selected']

        return actions

    def url_for_model_changelist(self, request, model):
        # used in add_extra_context
        return reverse('admin:%s_%s_changelist' % (model._meta.app_label, model._meta.model_name), current_app=model._meta.app_label)

    def add_extra_context(self, request, extra_context):
        # allow custom application breadcrumb url and name
        extra_context["custom_app_breadcrumb_url"] = getattr(
            self, "custom_app_breadcrumb_url", None)
        extra_context["custom_app_breadcrumb_name"] = getattr(
            self, "custom_app_breadcrumb_name", None)
        extra_context["custom_changelist_breadcrumb_url"] = getattr(
            self, "custom_changelist_breadcrumb_url", None)

        # for Service admins to render their Administration page
        if getattr(self, "extracontext_registered_admins", False):
            admins = []
            for model, model_admin in admin.site._registry.items():
                if model == self.model:
                    continue
                if model._meta.app_label == self.model._meta.app_label:
                    info = {"app": model._meta.app_label,
                            "model": model._meta.model_name,
                            "name": capfirst(model._meta.verbose_name_plural),
                            "url": self.url_for_model_changelist(request, model)}
                    admins.append(info)
            extra_context["registered_admins"] = admins

    def change_view(self, request, object_id, extra_context=None):
        extra_context = extra_context or {}

        if self.__user_is_readonly(request):
            if not hasattr(self, "readonly_save"):
                # save the original readonly fields
                self.readonly_save = self.readonly_fields
                self.inlines_save = self.inlines
            if hasattr(self, "user_readonly_fields"):
                self.readonly_fields = self.user_readonly_fields
            if hasattr(self, "user_readonly_inlines"):
                self.inlines = self.user_readonly_inlines
        else:
            if hasattr(self, "readonly_save"):
                # restore the original readonly fields
                self.readonly_fields = self.readonly_save
            if hasattr(self, "inlines_save"):
                self.inlines = self.inlines_save

        self.add_extra_context(request, extra_context)

        try:
            return super(XOSAdminMixin, self).change_view(request, object_id, extra_context=extra_context)
        except PermissionDenied:
            pass
        except ValidationError as e:
            if (e.params is None):
                # Validation errors that don't reference a specific field will
                # often throw a non-descriptive 500 page to the user. The code
                # below will cause an error message to be printed and the
                # page refreshed instead.
                # As a side-effect it turns the request back into a 'GET' which
                # may wipe anything the user had changed on the page. But, at
                # least the user gets a real error message.
                # TODO: revisit this and display some kind of error view
                request.method = 'GET'
                messages.error(request, e.message)
                return super(XOSAdminMixin, self).change_view(request, object_id, extra_context=extra_context)
            else:
                raise
        if request.method == 'POST':
            raise PermissionDenied
        request.readonly = True
        return super(XOSAdminMixin, self).change_view(request, object_id, extra_context=extra_context)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        self.add_extra_context(request, extra_context)

        return super(XOSAdminMixin, self).changelist_view(request, extra_context=extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}

        self.add_extra_context(request, extra_context)

        return super(XOSAdminMixin, self).add_view(request, form_url, extra_context=extra_context)

    def __user_is_readonly(self, request):
        return request.user.isReadOnlyUser()

    def backend_status_text(self, obj):
        return mark_safe(backend_text(obj))

    def backend_status_icon(self, obj):
        return mark_safe(backend_icon(obj))
    backend_status_icon.short_description = ""

    def get_form(self, request, obj=None, **kwargs):
        # Save obj and request in thread-local storage, so suit_form_tabs can
        # use it to determine whether we're in edit or add mode, and can
        # determine whether the user is an admin.
        _thread_locals.request = request
        _thread_locals.obj = obj
        return super(XOSAdminMixin, self).get_form(request, obj, **kwargs)

    def get_inline_instances(self, request, obj=None):
        inlines = super(XOSAdminMixin, self).get_inline_instances(request, obj)

        # inlines that should only be shown to an admin user
        if request.user.is_admin:
            for inline_class in getattr(self, "admin_inlines", []):
                inlines.append(inline_class(self.model, self.admin_site))

        return inlines


class ReadOnlyAwareAdmin(XOSAdminMixin, admin.ModelAdmin):
    # Note: Make sure XOSAdminMixin is listed before
    # admin.ModelAdmin in the class declaration.

    pass


class XOSBaseAdmin(ReadOnlyAwareAdmin):
    save_on_top = False


class SingletonAdmin (ReadOnlyAwareAdmin):

    def has_add_permission(self, request):
        if not super(SingletonAdmin, self).has_add_permission(request):
            return False

        num_objects = self.model.objects.count()
        if num_objects >= 1:
            return False
        else:
            return True


class ServiceAppAdmin (SingletonAdmin):
    extracontext_registered_admins = True


class XOSTabularInline(admin.TabularInline):

    def __init__(self, *args, **kwargs):
        super(XOSTabularInline, self).__init__(*args, **kwargs)

        # InlineModelAdmin as no get_fields() method, so in order to add
        # the selflink field, we override __init__ to modify self.fields and
        # self.readonly_fields.

        self.setup_selflink()

    @property
    def selflink_model(self):
        if hasattr(self, "selflink_fieldname"):
            """ self.selflink_model can be defined to punch through a relation
                to its target object. For example, in SliceNetworkInline, set
                selflink_model = "network", and the URL will lead to the Network
                object instead of trying to bring up a change view of the
                SliceNetwork object.
            """
            return getattr(self.model, self.selflink_fieldname).field.rel.to
        else:
            return self.model

    @property
    def selflink_reverse_path(self):
        return "admin:%s_change" % (self.selflink_model._meta.db_table)

    def get_change_url(self, id):
        """ Get the URL to a change form in the admin for this model """
        reverse_path = self.selflink_reverse_path  # "admin:%s_change" % (self.selflink_model._meta.db_table)
        try:
            url = reverse(reverse_path, args=(id,))
        except NoReverseMatch:
            return None

        return url

    def setup_selflink(self):
        url = self.get_change_url(0)

        # We don't have an admin for this object, so don't create the
        # selflink.
        if (url == None):
            return

        # Since we need to add "selflink" to the field list, we need to create
        # self.fields if it is None.
        if (self.fields is None):
            self.fields = []
            for f in self.model._meta.fields:
                if f.editable and f.name != "id":
                    self.fields.append(f.name)

        self.fields = tuple(self.fields) + ("selflink", )

        if self.readonly_fields is None:
            self.readonly_fields = ()

        self.readonly_fields = tuple(self.readonly_fields) + ("selflink", )

    def selflink(self, obj):
        if hasattr(self, "selflink_fieldname"):
            obj = getattr(obj, self.selflink_fieldname)

        if obj.id:
            url = self.get_change_url(obj.id)
            return "<a href='%s'>Details</a>" % str(url)
        else:
            return "Not present"

    selflink.allow_tags = True
    selflink.short_description = "Details"

    def has_add_permission(self, request):
        return not request.user.isReadOnlyUser()

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(self.readonly_fields)[:]
        if request.user.isReadOnlyUser():
            for field in self.fields:
                if not field in readonly_fields:
                    readonly_fields.append(field)
        return readonly_fields

    def backend_status_icon(self, obj):
        return mark_safe(backend_icon(obj))
    backend_status_icon.short_description = ""


class PlStackGenericTabularInline(generic.GenericTabularInline):

    def has_add_permission(self, request):
        return not request.user.isReadOnlyUser()

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(self.readonly_fields)[:]
        if request.user.isReadOnlyUser():
            for field in self.fields:
                if not field in readonly_fields:
                    readonly_fields.append(field)
        return readonly_fields

    def backend_status_icon(self, obj):
        return mark_safe(backend_icon(obj))
    backend_status_icon.short_description = ""


class ReservationInline(XOSTabularInline):
    model = Reservation
    extra = 0
    suit_classes = 'suit-tab suit-tab-reservations'

    def queryset(self, request):
        return Reservation.select_by_user(request.user)


class TagInline(PlStackGenericTabularInline):
    model = Tag
    extra = 0
    suit_classes = 'suit-tab suit-tab-tags'
    fields = ['service', 'name', 'value']

    def queryset(self, request):
        return Tag.select_by_user(request.user)


class InstanceInline(XOSTabularInline):
    model = Instance
    fields = ['backend_status_icon', 'all_ips_string', 'instance_id',
              'instance_name', 'slice', 'deployment', 'flavor', 'image', 'node']
    extra = 0
    max_num = 0
    readonly_fields = ['backend_status_icon', 'all_ips_string', 'instance_id',
                       'instance_name', 'slice', 'deployment', 'flavor', 'image', 'node']
    suit_classes = 'suit-tab suit-tab-instances'

    def queryset(self, request):
        return Instance.select_by_user(request.user)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'deployment':
            kwargs['queryset'] = Deployment.select_by_acl(request.user).filter(
                sitedeployments__nodes__isnull=False).distinct()
            kwargs['widget'] = forms.Select(
                attrs={'onChange': "instance_deployment_changed(this);"})
        if db_field.name == 'flavor':
            kwargs['widget'] = forms.Select(
                attrs={'onChange': "instance_flavor_changed(this);"})

        field = super(InstanceInline, self).formfield_for_foreignkey(
            db_field, request, **kwargs)

        return field


class CordInstanceInline(XOSTabularInline):
    model = Instance
    fields = ['backend_status_icon', 'all_ips_string', 'instance_id',
              'instance_name', 'slice', 'flavor', 'image', 'node']
    extra = 0
    readonly_fields = ['backend_status_icon',
                       'all_ips_string', 'instance_id', 'instance_name']
    suit_classes = 'suit-tab suit-tab-instances'

    def queryset(self, request):
        return Instance.select_by_user(request.user)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'deployment':

            kwargs['queryset'] = Deployment.select_by_acl(request.user).filter(
                sitedeployments__nodes__isnull=False).distinct()
            kwargs['widget'] = forms.Select(
                attrs={'onChange': "instance_deployment_changed(this);"})
        if db_field.name == 'flavor':
            kwargs['widget'] = forms.Select(
                attrs={'onChange': "instance_flavor_changed(this);"})

        field = super(CordInstanceInline, self).formfield_for_foreignkey(
            db_field, request, **kwargs)

        return field


class SiteInline(XOSTabularInline):
    model = Site
    extra = 0
    suit_classes = 'suit-tab suit-tab-sites'

    def queryset(self, request):
        return Site.select_by_user(request.user)


class SiteHostsNodesInline(SiteInline):

    def queryset(self, request):
        return Site.select_by_user(request.user).filter(hosts_nodes=True)


class SiteHostsUsersInline(SiteInline):

    def queryset(self, request):
        return Site.select_by_user(request.user).filter(hosts_users=True)


class UserInline(XOSTabularInline):
    model = User
    fields = ['backend_status_icon', 'email', 'firstname', 'lastname']
    readonly_fields = ('backend_status_icon', )
    extra = 0
    suit_classes = 'suit-tab suit-tab-users'

    def queryset(self, request):
        return User.select_by_user(request.user)


class SliceInline(XOSTabularInline):
    model = Slice
    fields = ['backend_status_icon', 'name', 'site', 'serviceClass', 'service']
    readonly_fields = ('backend_status_icon', )
    extra = 0
    suit_classes = 'suit-tab suit-tab-slices'

    def queryset(self, request):
        return Slice.select_by_user(request.user)


class NodeInline(XOSTabularInline):
    model = Node
    extra = 0
    suit_classes = 'suit-tab suit-tab-nodes'
    fields = ['backend_status_icon', 'name', 'site_deployment']
    readonly_fields = ('backend_status_icon', )


class DeploymentPrivilegeInline(XOSTabularInline):
    model = DeploymentPrivilege
    extra = 0
    suit_classes = 'suit-tab suit-tab-deploymentprivileges'
    fields = ['backend_status_icon', 'user', 'role', 'deployment']
    readonly_fields = ('backend_status_icon', )

    def queryset(self, request):
        return DeploymentPrivilege.select_by_user(request.user)


class ControllerSiteInline(XOSTabularInline):
    model = ControllerSite
    extra = 0
    suit_classes = 'suit-tab suit-tab-admin-only'
    fields = ['controller', 'site', 'tenant_id']


class SitePrivilegeInline(XOSTabularInline):
    model = SitePrivilege
    extra = 0
    suit_classes = 'suit-tab suit-tab-siteprivileges'
    fields = ['backend_status_icon', 'user', 'site', 'role']
    readonly_fields = ('backend_status_icon', )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'site':
            kwargs['queryset'] = Site.select_by_user(request.user)

        if db_field.name == 'user':
            kwargs['queryset'] = User.select_by_user(request.user)
        return super(SitePrivilegeInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def queryset(self, request):
        return SitePrivilege.select_by_user(request.user)


class ServicePrivilegeInline(XOSTabularInline):
    model = ServicePrivilege
    extra = 0
    suit_classes = 'suit-tab suit-tab-serviceprivileges'
    fields = ['backend_status_icon', 'user', 'service', 'role']
    readonly_fields = ('backend_status_icon', )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'service':
            kwargs['queryset'] = Service.select_by_user(request.user)
        if db_field.name == 'user':
            kwargs['queryset'] = User.select_by_user(request.user)
        return super(ServicePrivilegeInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def queryset(self, request):
        return ServicePrivilege.select_by_user(request.user)


class SiteDeploymentInline(XOSTabularInline):
    model = SiteDeployment
    extra = 0
    suit_classes = 'suit-tab suit-tab-sitedeployments'
    fields = ['backend_status_icon', 'deployment', 'site', 'controller']
    readonly_fields = ('backend_status_icon', )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'site':
            kwargs['queryset'] = Site.select_by_user(request.user)

        if db_field.name == 'deployment':
            kwargs['queryset'] = Deployment.select_by_user(request.user)

        if db_field.name == 'controller':
            if len(resolve(request.path).args) > 0:
                kwargs['queryset'] = Controller.select_by_user(request.user).filter(
                    deployment__id=int(resolve(request.path).args[0]))

        return super(SiteDeploymentInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def queryset(self, request):
        return SiteDeployment.select_by_user(request.user)


class SlicePrivilegeInline(XOSTabularInline):
    model = SlicePrivilege
    suit_classes = 'suit-tab suit-tab-sliceprivileges'
    extra = 0
    fields = ('backend_status_icon', 'user', 'slice', 'role')
    readonly_fields = ('backend_status_icon', )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'slice':
            kwargs['queryset'] = Slice.select_by_user(request.user)
        if db_field.name == 'user':
            # all users are available to be granted SlicePrivilege
            kwargs['queryset'] = User.objects.all()

        return super(SlicePrivilegeInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def queryset(self, request):
        return SlicePrivilege.select_by_user(request.user)


class SliceNetworkInline(XOSTabularInline):
    model = Network.slices.through
    selflink_fieldname = "network"
    extra = 0
    verbose_name = "Network Connection"
    verbose_name_plural = "Network Connections"
    suit_classes = 'suit-tab suit-tab-slicenetworks'
    fields = ['backend_status_icon', 'network']
    readonly_fields = ('backend_status_icon', )


class ImageDeploymentsInline(XOSTabularInline):
    model = ImageDeployments
    extra = 0
    verbose_name = "Image Deployments"
    verbose_name_plural = "Image Deployments"
    suit_classes = 'suit-tab suit-tab-imagedeployments'
    fields = ['backend_status_icon', 'image', 'deployment']
    readonly_fields = ['backend_status_icon']


class ControllerImagesInline(XOSTabularInline):
    model = ControllerImages
    extra = 0
    verbose_name = "Controller Images"
    verbose_name_plural = "Controller Images"
    suit_classes = 'suit-tab suit-tab-admin-only'
    fields = ['backend_status_icon', 'image', 'controller', 'glance_image_id']
    readonly_fields = ['backend_status_icon', 'glance_image_id']


class SliceRoleAdmin(XOSBaseAdmin):
    model = SliceRole
    pass


class SiteRoleAdmin(XOSBaseAdmin):
    model = SiteRole
    pass


class DeploymentAdminForm(forms.ModelForm):
    images = forms.ModelMultipleChoiceField(
        queryset=Image.objects.all(),
        required=False,
        help_text="Select which images should be deployed on this deployment",
        widget=FilteredSelectMultiple(
            verbose_name=('Images'), is_stacked=False
        )
    )
    flavors = forms.ModelMultipleChoiceField(
        queryset=Flavor.objects.all(),
        required=False,
        help_text="Select which flavors should be usable on this deployment",
        widget=FilteredSelectMultiple(
            verbose_name=('Flavors'), is_stacked=False
        )
    )

    class Meta:
        model = Deployment
        many_to_many = ["flavors", ]

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super(DeploymentAdminForm, self).__init__(*args, **kwargs)

        self.fields['accessControl'].initial = "allow site " + \
            request.user.site.name

        if self.instance and self.instance.pk:
            self.fields['images'].initial = [
                x.image for x in self.instance.imagedeployments.all()]
            self.fields['flavors'].initial = self.instance.flavors.all()

    def manipulate_m2m_objs(self, this_obj, selected_objs, all_relations, relation_class, local_attrname, foreign_attrname):
        """ helper function for handling m2m relations from the MultipleChoiceField

            this_obj: the source object we want to link from

            selected_objs: a list of destination objects we want to link to

            all_relations: the full set of relations involving this_obj, including ones we don't want

            relation_class: the class that implements the relation from source to dest

            local_attrname: field name representing this_obj in relation_class

            foreign_attrname: field name representing selected_objs in relation_class

            This function will remove all newobjclass relations from this_obj
            that are not contained in selected_objs, and add any relations that
            are in selected_objs but don't exist in the data model yet.
        """

        existing_dest_objs = []
        for relation in list(all_relations):
            if getattr(relation, foreign_attrname) not in selected_objs:
                # print "deleting site", sdp.site
                relation.delete()
            else:
                existing_dest_objs.append(getattr(relation, foreign_attrname))

        for dest_obj in selected_objs:
            if dest_obj not in existing_dest_objs:
                # print "adding site", site
                kwargs = {foreign_attrname: dest_obj, local_attrname: this_obj}
                relation = relation_class(**kwargs)
                relation.save()

    def save(self, commit=True):
        deployment = super(DeploymentAdminForm, self).save(commit=False)

        if commit:
            deployment.save()
            # this has to be done after save() if/when a deployment is first
            # created
            deployment.flavors = self.cleaned_data['flavors']

        if deployment.pk:
            # save_m2m() doesn't seem to work with 'through' relations. So we
            #    create/destroy the through models ourselves. There has to be
            #    a better way...

            self.manipulate_m2m_objs(deployment, self.cleaned_data[
                                     'images'], deployment.imagedeployments.all(), ImageDeployments, "deployment", "image")
            # manipulate_m2m_objs doesn't work for Flavor/Deployment relationship
            # so well handle that manually here
            for flavor in deployment.flavors.all():
                if getattr(flavor, 'name') not in self.cleaned_data['flavors']:
                    deployment.flavors.remove(flavor)
            for flavor in self.cleaned_data['flavors']:
                if flavor not in deployment.flavors.all():
                    flavor.deployments.add(deployment)

        self.save_m2m()

        return deployment


class DeploymentAdminROForm(DeploymentAdminForm):

    def save(self, commit=True):
        raise PermissionDenied


class SiteAssocInline(XOSTabularInline):
    model = Site.deployments.through
    extra = 0
    suit_classes = 'suit-tab suit-tab-sites'


class DeploymentAdmin(XOSBaseAdmin):
    model = Deployment
    fieldList = ['backend_status_text', 'name',
                 'images', 'flavors', 'accessControl']
    fieldsets = [
        (None, {'fields': fieldList, 'classes': ['suit-tab suit-tab-general']})]
    # node no longer directly connected to deployment
    #inlines = [DeploymentPrivilegeInline,NodeInline,TagInline,ImageDeploymentsInline]
    inlines = [DeploymentPrivilegeInline, TagInline,
               ImageDeploymentsInline, SiteDeploymentInline]
    list_display = ['backend_status_icon', 'name']
    list_display_links = ('backend_status_icon', 'name', )
    readonly_fields = ('backend_status_text', )

    user_readonly_fields = ['name']

    # nodes no longer direclty connected to deployments
    suit_form_tabs = (('general', 'Deployment Details'),
                      ('deploymentprivileges', 'Privileges'), ('sitedeployments', 'Sites'))

    def get_form(self, request, obj=None, **kwargs):
        if request.user.isReadOnlyUser() or not request.user.is_admin:
            kwargs["form"] = DeploymentAdminROForm
        else:
            kwargs["form"] = DeploymentAdminForm
        adminForm = super(DeploymentAdmin, self).get_form(
            request, obj, **kwargs)

        # from stackexchange: pass the request object into the form

        class AdminFormMetaClass(adminForm):

            def __new__(cls, *args, **kwargs):
                kwargs['request'] = request
                return adminForm(*args, **kwargs)

        return AdminFormMetaClass


class ControllerAdminForm(forms.ModelForm):
    backend_disabled = forms.BooleanField(required=False)

    class Meta:
        model = Controller

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super(ControllerAdminForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['backend_disabled'].initial = self.instance.get_backend_register(
                'disabled', False)
        else:
            # defaults when adding new controller
            self.fields['backend_disabled'].initial = False

    def save(self, commit=True):
        self.instance.set_backend_register(
            "disabled", self.cleaned_data["backend_disabled"])
        return super(ControllerAdminForm, self).save(commit=commit)


class ControllerAdmin(XOSBaseAdmin):
    model = Controller
    fieldList = ['deployment', 'name', 'backend_type', 'backend_disabled', 'version', 'auth_url', 'admin_user',
                 'admin_tenant', 'admin_password', 'domain', 'rabbit_host', 'rabbit_user', 'rabbit_password']
    fieldsets = [
        (None, {'fields': fieldList, 'classes': ['suit-tab suit-tab-general']})]
    inlines = [ControllerSiteInline]  # ,ControllerImagesInline]
    list_display = ['backend_status_icon', 'name', 'version', 'backend_type']
    list_display_links = ('backend_status_icon', 'name', )
    readonly_fields = ('backend_status_text',)
    form = ControllerAdminForm

    user_readonly_fields = []

    def save_model(self, request, obj, form, change):
            # update openstack connection to use this site/tenant
        obj.save_by_user(request.user)

    def delete_model(self, request, obj):
        obj.delete_by_user(request.user)

    def queryset(self, request):
        return Controller.select_by_user(request.user)

    @property
    def suit_form_tabs(self):
        tabs = [('general', 'Controller Details'),
                ]

        request = getattr(_thread_locals, "request", None)
        if request and request.user.is_admin:
            tabs.append(('admin-only', 'Admin-Only'))

        return tabs


class TenantAttributeAdmin(XOSBaseAdmin):
    model = TenantAttribute
    list_display = ('backend_status_icon', 'tenant', 'name', 'value')
    list_display_links = ('backend_status_icon', 'name')
    fieldList = ('backend_status_text', 'tenant', 'name', 'value', )
    fieldsets = [
        (None, {'fields': fieldList, 'classes': ['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', )

    suit_form_tabs = (('general', 'Tenant Root Details'),
                      )


class TenantAttrAsTabInline(XOSTabularInline):
    model = TenantAttribute
    fields = ['name', 'value']
    extra = 0
    suit_classes = 'suit-tab suit-tab-tenantattrs'


class TenantRootRoleAdmin(XOSBaseAdmin):
    model = TenantRootRole
    fields = ('role',)


class TenantRootTenantInline(XOSTabularInline):
    model = Tenant
    fields = ['provider_service', 'subscriber_root']
    extra = 0
    suit_classes = 'suit-tab suit-tab-tenantroots'
    fk_name = 'subscriber_root'
    verbose_name = 'subscribed tenant'
    verbose_name_plural = 'subscribed tenants'

    # def queryset(self, request):
    #    qs = super(TenantRootTenantInline, self).queryset(request)
    #    return qs.filter(kind="coarse")


class TenantRootPrivilegeInline(XOSTabularInline):
    model = TenantRootPrivilege
    extra = 0
    suit_classes = 'suit-tab suit-tab-tenantrootprivileges'
    fields = ['backend_status_icon', 'user', 'role', 'tenant_root']
    readonly_fields = ('backend_status_icon', )

    def queryset(self, request):
        return TenantRootPrivilege.select_by_user(request.user)


class TenantRootAdmin(XOSBaseAdmin):
    model = TenantRoot
    list_display = ('backend_status_icon', 'name', 'kind')
    list_display_links = ('backend_status_icon', 'name')
    fieldList = ('backend_status_text', 'name', 'kind', )
    fieldsets = [
        (None, {'fields': fieldList, 'classes': ['suit-tab suit-tab-general']})]
    inlines = (TenantRootTenantInline, TenantRootPrivilegeInline)
    readonly_fields = ('backend_status_text', )

    suit_form_tabs = (('general', 'Tenant Root Details'),
                      ('tenantroots', 'Tenancy'),
                      ('tenantrootprivileges', 'Privileges')
                      )


class TenantRoleAdmin(XOSBaseAdmin):
    """Admin for TenantRoles."""
    model = TenantRole
    fields = ('role',)


class TenantPrivilegeInline(XOSTabularInline):
    """Inline for adding a TenantPrivilege to a Tenant."""
    model = TenantPrivilege
    extra = 0
    suit_classes = 'suit-tab suit-tab-tenantprivileges'
    fields = ['backend_status_icon', 'user', 'role', 'tenant']
    readonly_fields = ('backend_status_icon', )

    def queryset(self, request):
        return TenantPrivilege.select_by_user(request.user)


class ProviderTenantInline(XOSTabularInline):
    model = CoarseTenant
    fields = ['provider_service', 'subscriber_service', 'connect_method']
    extra = 0
    suit_classes = 'suit-tab suit-tab-servicetenants'
    fk_name = 'provider_service'
    verbose_name = 'provided tenant'
    verbose_name_plural = 'provided tenants'

    def queryset(self, request):
        qs = super(ProviderTenantInline, self).queryset(request)
        return qs.filter(kind="coarse")


class SubscriberTenantInline(XOSTabularInline):
    model = CoarseTenant
    fields = ['provider_service', 'subscriber_service', 'connect_method']
    extra = 0
    suit_classes = 'suit-tab suit-tab-servicetenants'
    fk_name = 'subscriber_service'
    verbose_name = 'subscribed tenant'
    verbose_name_plural = 'subscribed tenants'

    def queryset(self, request):
        qs = super(SubscriberTenantInline, self).queryset(request)
        return qs.filter(kind="coarse")


class ServiceAttrAsTabInline(XOSTabularInline):
    model = ServiceAttribute
    fields = ['name', 'value']
    extra = 0
    suit_classes = 'suit-tab suit-tab-serviceattrs'


class ServiceAdmin(XOSBaseAdmin):
    list_display = ("backend_status_icon", "name", "kind",
                    "versionNumber", "enabled", "published")
    list_display_links = ('backend_status_icon', 'name', )
    fieldList = ["backend_status_text", "name", "kind", "description", "controller", "versionNumber", "enabled", "published",
                 "view_url", "icon_url", "public_key", "private_key_fn", "service_specific_attribute", "service_specific_id"]
    fieldsets = [
        (None, {'fields': fieldList, 'classes': ['suit-tab suit-tab-general']})]
    inlines = [ServiceAttrAsTabInline, SliceInline, ProviderTenantInline,
               SubscriberTenantInline, ServicePrivilegeInline]
    readonly_fields = ('backend_status_text', )

    user_readonly_fields = fieldList

    suit_form_tabs = (('general', 'Service Details'),
                      ('slices', 'Slices'),
                      ('serviceattrs', 'Additional Attributes'),
                      ('servicetenants', 'Tenancy'),
                      ('serviceprivileges', 'Privileges')
                      )

class ServiceControllerResourceInline(XOSTabularInline):
    model = ServiceControllerResource
    fields = ['name', 'kind', 'format', 'url']
    extra = 0
    suit_classes = 'suit-tab suit-tab-resources'

class ServiceControllerAdmin(XOSBaseAdmin):
    list_display = ("backend_status_icon", "name",)
    list_display_links = ('backend_status_icon', 'name',)
    fieldList = ["backend_status_text", "name", "xos", "base_url", "synchronizer_run", "synchronizer_config"]
    fieldsets = [
        (None, {'fields': fieldList, 'classes': ['suit-tab suit-tab-general']})]
    inlines = [ServiceControllerResourceInline]
    readonly_fields = ('backend_status_text', )

    user_readonly_fields = fieldList

    suit_form_tabs = (('general', 'Service Details'),
                      ('resources', 'Resources'),
                      )


class SiteNodeInline(XOSTabularInline):
    model = Node
    fields = ['name', 'site_deployment']
    extra = 0
    suit_classes = 'suit-tab suit-tab-nodes'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # only display site deployments associated with this site
        if db_field.name == 'site_deployment':
            kwargs['queryset'] = SiteDeployment.objects.filter(
                site__id=int(request.path.split('/')[-2]))

        return super(SiteNodeInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


class SiteAdmin(XOSBaseAdmin):
    #fieldList = ['backend_status_text', 'name', 'site_url', 'enabled', 'is_public', 'login_base', 'accountLink','location']
    fieldList = ['backend_status_text', 'name', 'site_url', 'enabled',
                 'login_base', 'location', 'is_public', 'hosts_nodes', 'hosts_users']
    fieldsets = [
        (None, {'fields': fieldList, 'classes': [
         'suit-tab suit-tab-general']}),
        #('Deployment Networks', {'fields': ['deployments'], 'classes':['suit-tab suit-tab-deployments']}),
    ]
    #readonly_fields = ['backend_status_text', 'accountLink']
    readonly_fields = ['backend_status_text']

    #user_readonly_fields = ['name', 'deployments','site_url', 'enabled', 'is_public', 'login_base', 'accountLink']
    user_readonly_fields = ['name', 'deployments', 'site_url',
                            'enabled', 'is_public', 'login_base', 'hosts_nodes', 'hosts_users']

    list_display = ('backend_status_icon', 'name',
                    'login_base', 'site_url', 'enabled')
    list_display_links = ('backend_status_icon', 'name', )
    filter_horizontal = ('deployments',)
    inlines = [SliceInline, UserInline, TagInline,
               SitePrivilegeInline, SiteNodeInline]
    admin_inlines = [ControllerSiteInline]
    search_fields = ['name']

    @property
    def suit_form_tabs(self):
        tabs = [('general', 'Site Details'),
                ('users', 'Users'),
                ('siteprivileges', 'Privileges'),
                ('slices', 'Slices'),
                ('nodes', 'Nodes'),
                ]

        request = getattr(_thread_locals, "request", None)
        if request and request.user.is_admin:
            tabs.append(('admin-only', 'Admin-Only'))

        return tabs

    def queryset(self, request):
        return Site.select_by_user(request.user)

    def get_formsets(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            # hide MyInline in the add view
            if obj is None:
                continue
            if isinstance(inline, InstanceInline):
                inline.model.caller = request.user
            yield inline.get_formset(request, obj)

    def accountLink(self, obj):
        link_obj = obj.accounts.all()
        if link_obj:
            reverse_path = "admin:core_account_change"
            url = reverse(reverse_path, args=(link_obj[0].id,))
            return "<a href='%s'>%s</a>" % (url, "view billing details")
        else:
            return "no billing data for this site"
    accountLink.allow_tags = True
    accountLink.short_description = "Billing"

    def save_model(self, request, obj, form, change):
        # update openstack connection to use this site/tenant
        obj.save_by_user(request.user)

    def delete_model(self, request, obj):
        obj.delete_by_user(request.user)


class SitePrivilegeAdmin(XOSBaseAdmin):
    fieldList = ['backend_status_text', 'user', 'site', 'role']
    fieldsets = [
        (None, {'fields': fieldList, 'classes': ['collapse']})
    ]
    readonly_fields = ('backend_status_text', )
    list_display = ('backend_status_icon', 'user', 'site', 'role')
    list_display_links = list_display
    user_readonly_fields = fieldList
    user_readonly_inlines = []

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'site':
            if not request.user.is_admin:
                # only show sites where user is an admin or pi
                sites = set()
                for site_privilege in SitePrivilege.objects.filer(user=request.user):
                    if site_privilege.role.role_type in ['admin', 'pi']:
                        sites.add(site_privilege.site)
                kwargs['queryset'] = Site.objects.filter(site__in=list(sites))

        if db_field.name == 'user':
            if not request.user.is_admin:
                # only show users from sites where caller has admin or pi role
                roles = Role.objects.filter(role_type__in=['admin', 'pi'])
                site_privileges = SitePrivilege.objects.filter(
                    user=request.user).filter(role__in=roles)
                sites = [site_privilege.site for site_privilege in site_privileges]
                site_privileges = SitePrivilege.objects.filter(site__in=sites)
                emails = [
                    site_privilege.user.email for site_privilege in site_privileges]
                users = User.objects.filter(email__in=emails)
                kwargs['queryset'] = users

        return super(SitePrivilegeAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def queryset(self, request):
        # admins can see all privileges. Users can only see privileges at sites
        # where they have the admin role or pi role.
        qs = super(SitePrivilegeAdmin, self).queryset(request)
        # if not request.user.is_admin:
        #    roles = Role.objects.filter(role_type__in=['admin', 'pi'])
        #    site_privileges = SitePrivilege.objects.filter(user=request.user).filter(role__in=roles)
        #    login_bases = [site_privilege.site.login_base for site_privilege in site_privileges]
        #    sites = Site.objects.filter(login_base__in=login_bases)
        #    qs = qs.filter(site__in=sites)
        return qs


class SliceForm(forms.ModelForm):

    class Meta:
        model = Slice
        widgets = {
            'service': LinkedSelect
        }

    def clean(self):
        cleaned_data = super(SliceForm, self).clean()
        name = cleaned_data.get('name')
        site = cleaned_data.get('site')
        slice_id = self.instance.id
        if not site and slice_id:
            site = Slice.objects.get(id=slice_id).site
        if (not isinstance(site, Site)):
            # previous code indicates 'site' could be a site_id and not a site?
            site = Slice.objects.get(id=site.id)
        if not name.startswith(site.login_base):
            raise forms.ValidationError(
                'slice name must begin with %s' % site.login_base)
        return cleaned_data


class ControllerSliceInline(XOSTabularInline):
    model = ControllerSlice
    extra = 0
    verbose_name = "Controller Slices"
    verbose_name_plural = "Controller Slices"
    suit_classes = 'suit-tab suit-tab-admin-only'
    fields = ['backend_status_icon', 'controller', 'tenant_id']
    readonly_fields = ('backend_status_icon', 'controller')


class SliceAdmin(XOSBaseAdmin):
    form = SliceForm
    fieldList = ['backend_status_text', 'site', 'name', 'serviceClass', 'enabled',
                 'description', 'service', 'slice_url', 'max_instances', "default_isolation", "default_image", "network"]
    fieldsets = [('Slice Details', {'fields': fieldList, 'classes': [
                  'suit-tab suit-tab-general']}), ]
    readonly_fields = ('backend_status_text', )
    list_display = ('backend_status_icon', 'name', 'site',
                    'serviceClass', 'slice_url', 'max_instances')
    list_display_links = ('backend_status_icon', 'name', )
    normal_inlines = [SlicePrivilegeInline, InstanceInline,
                      TagInline, ReservationInline, SliceNetworkInline]
    inlines = normal_inlines
    admin_inlines = [ControllerSliceInline]
    suit_form_includes = (('slice_instance_tab.html', 'bottom', 'instances'),)

    user_readonly_fields = fieldList

    @property
    def suit_form_tabs(self):
        tabs = [('general', 'Slice Details'),
                ('slicenetworks', 'Networks'),
                ('sliceprivileges', 'Privileges'),
                ('instances', 'Instances'),
                #('reservations','Reservations'),
                ('tags', 'Tags'),
                ]

        request = getattr(_thread_locals, "request", None)
        if request and request.user.is_admin:
            tabs.append(('admin-only', 'Admin-Only'))

        return tabs

    def add_view(self, request, form_url='', extra_context=None):
        # Ugly hack for CORD
        self.inlines = self.normal_inlines
        # revert to default read-only fields
        self.readonly_fields = ('backend_status_text',)
        return super(SliceAdmin, self).add_view(request, form_url, extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        # cannot change the site of an existing slice so make the site field
        # read only
        if object_id:
            self.readonly_fields = ('backend_status_text', 'site')

        return super(SliceAdmin, self).change_view(request, object_id, form_url)

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        deployment_nodes = []
        for node in Node.objects.all():
            deployment_nodes.append(
                (node.site_deployment.deployment.id, node.id, node.name))

        deployment_flavors = []
        for flavor in Flavor.objects.all():
            for deployment in flavor.deployments.all():
                deployment_flavors.append(
                    (deployment.id, flavor.id, flavor.name))

        deployment_images = []
        for image in Image.objects.all():
            for deployment_image in image.imagedeployments.all():
                deployment_images.append(
                    (deployment_image.deployment.id, image.id, image.name))

        site_login_bases = []
        for site in Site.objects.all():
            site_login_bases.append((site.id, site.login_base))

        context["deployment_nodes"] = deployment_nodes
        context["deployment_flavors"] = deployment_flavors
        context["deployment_images"] = deployment_images
        context["site_login_bases"] = site_login_bases
        return super(SliceAdmin, self).render_change_form(request, context, add, change, form_url, obj)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'site':
            kwargs['queryset'] = Site.select_by_user(
                request.user).filter(hosts_users=True)
            kwargs['widget'] = forms.Select(
                attrs={'onChange': "update_slice_prefix(this, $($(this).closest('fieldset')[0]).find('.field-name input')[0].id)"})

        return super(SliceAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def queryset(self, request):
        # admins can see all keys. Users can only see slices they belong to.
        return Slice.select_by_user(request.user)

    def get_formsets(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            # hide MyInline in the add view
            if obj is None:
                continue
            if isinstance(inline, InstanceInline):
                inline.model.caller = request.user
            yield inline.get_formset(request, obj)

    def add_extra_context(self, request, extra_context):
        super(SliceAdmin, self).add_extra_context(request, extra_context)
        # set context["slice_id"] to the PK passed in the URL to this view
        if len(request.resolver_match.args) > 0:
            extra_context["slice_id"] = request.resolver_match.args[0]

    def UNUSED_get_inline_instances(self, request, obj=None):
        # HACK for CORD to do something special on vcpe slice page
        #    this was a good idea, but failed miserably, as something still
        #    expects there to be a deployment field.
        #    XXX this approach is better than clobbering self.inlines, so
        #    try to make this work post-demo.
        if (obj is not None) and (obj.name == "mysite_vcpe"):
            cord_vcpe_inlines = [SlicePrivilegeInline, CordInstanceInline,
                                 TagInline, ReservationInline, SliceNetworkInline]

            inlines = []
            for inline_class in cord_vcpe_inlines:
                inlines.append(inline_class(self.model, self.admin_site))
        else:
            inlines = super(SliceAdmin, self).get_inline_instances(
                request, obj)

        return inlines


class SlicePrivilegeAdmin(XOSBaseAdmin):
    fieldsets = [
        (None, {'fields': ['backend_status_text', 'user', 'slice', 'role']})
    ]
    readonly_fields = ('backend_status_text', )
    list_display = ('backend_status_icon', 'user', 'slice', 'role')
    list_display_links = list_display

    user_readonly_fields = ['user', 'slice', 'role']
    user_readonly_inlines = []

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'slice':
            kwargs['queryset'] = Slice.select_by_user(request.user)

        if db_field.name == 'user':
            kwargs['queryset'] = User.select_by_user(request.user)

        return super(SlicePrivilegeAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def queryset(self, request):
        # admins can see all memberships. Users can only see memberships of
        # slices where they have the admin role.
        return SlicePrivilege.select_by_user(request.user)

    def save_model(self, request, obj, form, change):
        # update openstack connection to use this site/tenant
        auth = request.session.get('auth', {})
        auth['tenant'] = obj.slice.slicename
        obj.os_manager = OpenStackManager(auth=auth, caller=request.user)
        obj.save()

    def delete_model(self, request, obj):
        # update openstack connection to use this site/tenant
        auth = request.session.get('auth', {})
        auth['tenant'] = obj.slice.slicename
        obj.os_manager = OpenStackManager(auth=auth, caller=request.user)
        obj.delete()


class ImageAdmin(XOSBaseAdmin):

    fieldsets = [('Image Details',
                  {'fields': ['backend_status_text', 'name', 'kind', 'disk_format', 'container_format', 'tag', 'path'],
                   'classes': ['suit-tab suit-tab-general']})
                 ]
    readonly_fields = ('backend_status_text', )

    suit_form_tabs = (('general', 'Image Details'), ('instances', 'Instances'),
                      ('imagedeployments', 'Deployments'), ('admin-only', 'Admin-Only'))

    inlines = [InstanceInline, ControllerImagesInline]

    user_readonly_fields = ['name', 'disk_format',
                            'container_format', 'tag', 'path']

    list_display = ['backend_status_icon', 'name', 'kind']
    list_display_links = ('backend_status_icon', 'name', )


class NodeForm(forms.ModelForm):
    nodelabels = forms.ModelMultipleChoiceField(
        queryset=NodeLabel.objects.all(),
        required=False,
        help_text="Select which labels apply to this node",
        widget=FilteredSelectMultiple(
            verbose_name=('Labels'), is_stacked=False
        )
    )

    class Meta:
        model = Node
        widgets = {
            'site': LinkedSelect,
            'deployment': LinkedSelect
        }

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super(NodeForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['nodelabels'].initial = self.instance.nodelabels.all()

    def save(self, commit=True):
        node = super(NodeForm, self).save(commit=False)

        node.nodelabels = self.cleaned_data['nodelabels']

        if commit:
            node.save()

        return node


class NodeLabelAdmin(XOSBaseAdmin):
    list_display = ('name',)
    list_display_links = ('name', )

    fields = ('name', )


class NodeAdmin(XOSBaseAdmin):
    form = NodeForm
    list_display = ('backend_status_icon', 'name', 'site_deployment')
    list_display_links = ('backend_status_icon', 'name', )
    list_filter = ('site_deployment',)

    inlines = [TagInline, InstanceInline]
    fieldsets = [('Node Details', {'fields': ['backend_status_text', 'name', 'site_deployment'], 'classes':['suit-tab suit-tab-details']}),
                 ('Labels', {'fields': ['nodelabels'], 'classes':['suit-tab suit-tab-labels']})]
    readonly_fields = ('backend_status_text', )

    user_readonly_fields = ['name', 'site_deployment']
    user_readonly_inlines = [TagInline, InstanceInline]

    suit_form_tabs = (('details', 'Node Details'), ('instances',
                                                    'Instances'), ('labels', 'Labels'), ('tags', 'Tags'))

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'site':
            kwargs['queryset'] = Site.select_by_user(
                request.user).filter(hosts_nodes=True)

        field = super(NodeAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)

        return field


class InstanceForm(forms.ModelForm):

    class Meta:
        model = Instance
        ip = forms.CharField(widget=PlainTextWidget)
        instance_name = forms.CharField(widget=PlainTextWidget)
        widgets = {
            'ip': PlainTextWidget(),
            'instance_name': PlainTextWidget(),
            'instance_id': PlainTextWidget(),
            'slice': LinkedSelect,
            'deployment': LinkedSelect,
            'node': LinkedSelect,
            'image': LinkedSelect
        }


class TagAdmin(XOSBaseAdmin):
    list_display = ['backend_status_icon', 'service',
                    'name', 'value', 'content_type', 'content_object', ]
    list_display_links = list_display
    user_readonly_fields = ['service', 'name',
                            'value', 'content_type', 'content_object', ]
    user_readonly_inlines = []


class InstancePortInline(XOSTabularInline):
    fields = ['backend_status_icon', 'network', 'instance', 'ip', 'mac']
    readonly_fields = ("backend_status_icon", "ip", "mac")
    model = Port
    #selflink_fieldname = "network"
    extra = 0
    verbose_name_plural = "Ports"
    verbose_name = "Port"
    suit_classes = 'suit-tab suit-tab-ports'


class InstanceAdmin(XOSBaseAdmin):
    form = InstanceForm
    fieldsets = [
        ('Instance Details', {'fields': ['backend_status_text', 'slice', 'deployment', 'isolation', 'flavor', 'image', 'node',
                                         'parent', 'all_ips_string', 'instance_id', 'instance_name', 'ssh_command', ], 'classes': ['suit-tab suit-tab-general'], }),
        ('Container Settings', {'fields': ['volumes'], 'classes': [
         'suit-tab suit-tab-container'], }),
    ]
    readonly_fields = ('backend_status_text', 'ssh_command', 'all_ips_string')
    list_display = ['backend_status_icon', 'all_ips_string', 'instance_id',
                    'instance_name', 'isolation', 'slice', 'flavor', 'image', 'node', 'deployment']
    list_display_links = ('backend_status_icon',
                          'all_ips_string', 'instance_id', )

    suit_form_tabs = (('general', 'Instance Details'), ('ports', 'Ports'),
                      ('container', 'Container Settings'), ('tags', 'Tags'))

    inlines = [TagInline, InstancePortInline]

    user_readonly_fields = ['slice', 'deployment',
                            'node', 'ip', 'instance_name', 'flavor', 'image']

    def ssh_command(self, obj):
        ssh_command = obj.get_ssh_command()
        if ssh_command:
            return ssh_command
        else:
            return "(not available)"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'slice':
            kwargs['queryset'] = Slice.select_by_user(request.user)

        return super(InstanceAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def queryset(self, request):
        # admins can see all instances. Users can only see instances of
        # the slices they belong to.
        return Instance.select_by_user(request.user)

    def add_view(self, request, form_url='', extra_context=None):
        self.readonly_fields = ('backend_status_text',
                                'ssh_command', 'all_ips_string')
        return super(InstanceAdmin, self).add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, extra_context=None):
        self.readonly_fields = ('backend_status_text', 'ssh_command',
                                'all_ips_string', 'deployment', 'slice', 'flavor', 'image', 'node')
        # for XOSAdminMixin.change_view's user_readonly_fields switching code
        self.readonly_save = self.readonly_fields
        return super(InstanceAdmin, self).change_view(request, object_id, extra_context)

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        deployment_nodes = []
#        for node in Node.objects.all():
        for node in Node.objects.order_by("name"):
            deployment_nodes.append(
                (node.site_deployment.deployment.id, node.id, node.name))

        deployment_flavors = []
        for flavor in Flavor.objects.all():
            for deployment in flavor.deployments.all():
                deployment_flavors.append(
                    (deployment.id, flavor.id, flavor.name))

        deployment_images = []
        for image in Image.objects.all():
            for deployment_image in image.imagedeployments.all():
                deployment_images.append(
                    (deployment_image.deployment.id, image.id, image.name))

        site_login_bases = []
        for site in Site.objects.all():
            site_login_bases.append((site.id, site.login_base))

        context["deployment_nodes"] = deployment_nodes
        context["deployment_flavors"] = deployment_flavors
        context["deployment_images"] = deployment_images
        context["site_login_bases"] = site_login_bases
        return super(InstanceAdmin, self).render_change_form(request, context, add, change, form_url, obj)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'deployment':
            kwargs['queryset'] = Deployment.select_by_acl(request.user).filter(
                sitedeployments__nodes__isnull=False).distinct()
            kwargs['widget'] = forms.Select(
                attrs={'onChange': "instance_deployment_changed(this);"})
        if db_field.name == 'flavor':
            kwargs['widget'] = forms.Select(
                attrs={'onChange': "instance_flavor_changed(this);"})

        field = super(InstanceAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs)

        return field

    # def save_model(self, request, obj, form, change):
    #    # update openstack connection to use this site/tenant
    #    auth = request.session.get('auth', {})
    #    auth['tenant'] = obj.slice.name
    #    obj.os_manager = OpenStackManager(auth=auth, caller=request.user)
    #    obj.creator = request.user
    #    obj.save()

    # def delete_model(self, request, obj):
    #    # update openstack connection to use this site/tenant
    #    auth = request.session.get('auth', {})
    #    auth['tenant'] = obj.slice.name
    #    obj.os_manager = OpenStackManager(auth=auth, caller=request.user)
    #    obj.delete()

# class ContainerPortInline(XOSTabularInline):
#    fields = ['backend_status_icon', 'network', 'container', 'ip', 'mac', 'segmentation_id']
#    readonly_fields = ("backend_status_icon", "ip", "mac", "segmentation_id")
#    model = Port
#    selflink_fieldname = "network"
#    extra = 0
#    verbose_name_plural = "Ports"
#    verbose_name = "Port"
#    suit_classes = 'suit-tab suit-tab-ports'

# class ContainerAdmin(XOSBaseAdmin):
#    fieldsets = [
#        ('Container Details', {'fields': ['backend_status_text', 'slice', 'node', 'docker_image', 'volumes', 'no_sync'], 'classes': ['suit-tab suit-tab-general'], })
#    ]
#    readonly_fields = ('backend_status_text', )
#    list_display = ['backend_status_icon', 'id']
#    list_display_links = ('backend_status_icon', 'id', )
#
#    suit_form_tabs =(('general', 'Container Details'), ('ports', 'Ports'))
#
#    inlines = [TagInline, ContainerPortInline]
#
#    def formfield_for_foreignkey(self, db_field, request, **kwargs):
#        if db_field.name == 'slice':
#            kwargs['queryset'] = Slice.select_by_user(request.user)
#
#        return super(ContainerAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
#
#    def queryset(self, request):
#        # admins can see all instances. Users can only see instances of
#        # the slices they belong to.
#        return Container.select_by_user(request.user)


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'firstname', 'lastname', 'phone', 'public_key')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.password = self.cleaned_data["password1"]
        # user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField(label='Password',
                                         help_text='<a href=\"password/\">Change Password</a>.')

    PROFILE_CHOICES = ((None, '------'), ('regular',
                                          'Regular user'), ('cp', 'Content Provider'))
    profile = forms.ChoiceField(
        choices=PROFILE_CHOICES, required=False, label="Quick Profile")

    class Meta:
        model = User
        widgets = {'public_key': UploadTextareaWidget, }

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

    def save(self, *args, **kwargs):
        if self.cleaned_data['profile']:
            self.instance.apply_profile(self.cleaned_data['profile'])

        return super(UserChangeForm, self).save(*args, **kwargs)


class UserDashboardViewInline(XOSTabularInline):
    model = UserDashboardView
    extra = 0
    suit_classes = 'suit-tab suit-tab-dashboards'
    fields = ['user', 'dashboardView', 'order']


class ControllerUserInline(XOSTabularInline):
    model = ControllerUser
    extra = 0
    suit_classes = 'suit-tab suit-tab-admin-only'
    fields = ['controller', 'user', 'kuser_id']


class UserAdmin(XOSAdminMixin, UserAdmin):
    # Note: Make sure XOSAdminMixin is listed before
    # admin.ModelAdmin in the class declaration.

    class Meta:
        app_label = "core"

    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('backend_status_icon', 'email',
                    'firstname', 'lastname', 'site', 'last_login')
    list_display_links = ("email",)
    list_filter = ('site',)
    inlines = [SlicePrivilegeInline, SitePrivilegeInline]
    admin_inlines = [ControllerUserInline]
    fieldListLoginDetails = ['backend_status_text', 'email', 'site', 'password', 'is_active',
                             'is_readonly', 'is_admin', 'is_appuser', 'public_key', 'login_page', 'profile']
    fieldListContactInfo = ['firstname', 'lastname', 'phone', 'timezone']

    fieldsets = (
        ('Login Details', {'fields': ['backend_status_text', 'email', 'site', 'password', 'is_active',
                                      'is_readonly', 'is_admin', 'is_appuser', 'public_key'], 'classes': ['suit-tab suit-tab-general']}),
        ('Contact Information', {'fields': (
            'firstname', 'lastname', 'phone', 'timezone'), 'classes': ['suit-tab suit-tab-contact']}),
        #('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('site', 'email', 'firstname', 'lastname', 'is_admin', 'is_readonly', 'is_appuser', 'phone', 'public_key', 'password1', 'password2')},
         ),
    )
    readonly_fields = ('backend_status_text', )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

    user_readonly_fields = fieldListLoginDetails + fieldListContactInfo

    @property
    def suit_form_tabs(self):
        if getattr(_thread_locals, "obj", None) is None:
            return []
        else:
            tabs = [('general', 'Login Details'),
                    ('contact', 'Contact Information'),
                    ('sliceprivileges', 'Slice Privileges'),
                    ('siteprivileges', 'Site Privileges')]

            request = getattr(_thread_locals, "request", None)
            if request and request.user.is_admin:
                tabs.append(('admin-only', 'Admin-Only'))

            return tabs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'site':
            kwargs['queryset'] = Site.select_by_user(
                request.user).filter(hosts_users=True)

        return super(UserAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def queryset(self, request):
        return User.select_by_user(request.user)

    def get_form(self, request, obj=None, **kwargs):
        # copy login details list
        login_details_fields = list(self.fieldListLoginDetails)
        if not request.user.is_admin:
            # only admins can see 'is_admin' and 'is_readonly' fields
            if 'is_admin' in login_details_fields:
                login_details_fields.remove('is_admin')
            if 'is_readonly' in login_details_fields:
                login_details_fields.remove('is_readonly')
            if 'is_appuser' in login_details_fields:
                login_details_fields.remove('is_admin')
            if 'profile' in login_details_fields:
                login_details_fields.remove('profile')
            # if len(request.user.siteprivileges.filter(role__role = 'pi')) > 0:
                # only admins and pis can change a user's site
            #    self.readonly_fields = ('backend_status_text', 'site')
        self.fieldsets = (
            ('Login Details', {'fields': login_details_fields,
                               'classes': ['suit-tab suit-tab-general']}),
            ('Contact Information', {
             'fields': self.fieldListContactInfo, 'classes': ['suit-tab suit-tab-contact']}),
        )
        return super(UserAdmin, self).get_form(request, obj, **kwargs)


class ControllerDashboardViewInline(XOSTabularInline):
    model = ControllerDashboardView
    extra = 0
    fields = ["controller", "url"]
    suit_classes = 'suit-tab suit-tab-controllers'


class DashboardViewAdmin(XOSBaseAdmin):
    fieldsets = [('Dashboard View Details',
                  {'fields': ['backend_status_text', 'name', 'url', 'enabled', 'deployments'],
                   'classes': ['suit-tab suit-tab-general']})
                 ]
    list_display = ["name", "enabled", "url"]
    readonly_fields = ('backend_status_text', )
    inlines = [ControllerDashboardViewInline]

    suit_form_tabs = (('general', 'Dashboard View Details'),
                      ('controllers', 'Per-controller Dashboard Details'))


class ServiceResourceInline(XOSTabularInline):
    model = ServiceResource
    extra = 0


class ServiceClassAdmin(XOSBaseAdmin):
    list_display = ('backend_status_icon', 'name',
                    'commitment', 'membershipFee')
    list_display_links = ('backend_status_icon', 'name', )
    inlines = [ServiceResourceInline]

    user_readonly_fields = ['name', 'commitment', 'membershipFee']
    user_readonly_inlines = []


class ReservedResourceInline(XOSTabularInline):
    model = ReservedResource
    extra = 0
    suit_classes = 'suit-tab suit-tab-reservedresources'

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super(ReservedResourceInline, self).formfield_for_foreignkey(
            db_field, request, **kwargs)

        if db_field.name == 'resource':
            # restrict resources to those that the slice's service class allows
            if request._slice is not None:
                field.queryset = field.queryset.filter(
                    serviceClass=request._slice.serviceClass, calendarReservable=True)
                if len(field.queryset) > 0:
                    field.initial = field.queryset.all()[0]
            else:
                field.queryset = field.queryset.none()
        elif db_field.name == 'instance':
            # restrict instances to those that belong to the slice
            if request._slice is not None:
                field.queryset = field.queryset.filter(slice=request._slice)
            else:
                field.queryset = field.queryset.none()

        return field

    def queryset(self, request):
        return ReservedResource.select_by_user(request.user)


class ReservationChangeForm(forms.ModelForm):

    class Meta:
        model = Reservation
        widgets = {
            'slice': LinkedSelect
        }


class ReservationAddForm(forms.ModelForm):
    slice = forms.ModelChoiceField(queryset=Slice.objects.all(), widget=forms.Select(
        attrs={"onChange": "document.getElementById('id_refresh').value=1; submit()"}))
    refresh = forms.CharField(widget=forms.HiddenInput())

    class Media:
        css = {'all': ('xos.css',)}   # .field-refresh { display: none; }

    def clean_slice(self):
        slice = self.cleaned_data.get("slice")
        x = ServiceResource.objects.filter(
            serviceClass=slice.serviceClass, calendarReservable=True)
        if len(x) == 0:
            raise forms.ValidationError(
                "The slice you selected does not have a service class that allows reservations")
        return slice

    class Meta:
        model = Reservation
        widgets = {
            'slice': LinkedSelect
        }


class ReservationAddRefreshForm(ReservationAddForm):
    """ This form is displayed when the Reservation Form receives an update
        from the Slice dropdown onChange handler. It doesn't validate the
        data and doesn't save the data. This will cause the form to be
        redrawn.
    """

    """ don't validate anything other than slice """
    dont_validate_fields = ("startTime", "duration")

    def full_clean(self):
        result = super(ReservationAddForm, self).full_clean()

        for fieldname in self.dont_validate_fields:
            if fieldname in self._errors:
                del self._errors[fieldname]

        return result

    """ don't save anything """

    def is_valid(self):
        return False


class ReservationAdmin(XOSBaseAdmin):
    fieldList = ['backend_status_text', 'slice', 'startTime', 'duration']
    fieldsets = [('Reservation Details', {
                  'fields': fieldList, 'classes': ['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', )
    list_display = ('startTime', 'duration')
    form = ReservationAddForm

    suit_form_tabs = (('general', 'Reservation Details'),
                      ('reservedresources', 'Reserved Resources'))

    inlines = [ReservedResourceInline]
    user_readonly_fields = fieldList

    def add_view(self, request, form_url='', extra_context=None):
        timezone.activate(request.user.timezone)
        request._refresh = False
        request._slice = None
        if request.method == 'POST':
            # "refresh" will be set to "1" if the form was submitted due to
            # a change in the Slice dropdown.
            if request.POST.get("refresh", "1") == "1":
                request._refresh = True
                request.POST["refresh"] = "0"

            # Keep track of the slice that was selected, so the
            # reservedResource inline can filter items for the slice.
            request._slice = request.POST.get("slice", None)
            if (request._slice is not None):
                request._slice = Slice.objects.get(id=request._slice)

        result = super(ReservationAdmin, self).add_view(
            request, form_url, extra_context)
        return result

    def changelist_view(self, request, extra_context=None):
        timezone.activate(request.user.timezone)
        return super(ReservationAdmin, self).changelist_view(request, extra_context)

    def get_form(self, request, obj=None, **kwargs):
        request._obj_ = obj
        if obj is not None:
            # For changes, set request._slice to the slice already set in the
            # object.
            request._slice = obj.slice
            self.form = ReservationChangeForm
        else:
            if getattr(request, "_refresh", False):
                self.form = ReservationAddRefreshForm
            else:
                self.form = ReservationAddForm
        return super(ReservationAdmin, self).get_form(request, obj, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        if (obj is not None):
            # Prevent slice from being changed after the reservation has been
            # created.
            return ['slice']
        else:
            return []

    def queryset(self, request):
        return Reservation.select_by_user(request.user)


class NetworkParameterTypeAdmin(XOSBaseAdmin):
    list_display = ("backend_status_icon", "name", )
    list_display_links = ('backend_status_icon', 'name', )
    user_readonly_fields = ['name']
    user_readonly_inlines = []


class RouterAdmin(XOSBaseAdmin):
    list_display = ("backend_status_icon", "name", )
    list_display_links = ('backend_status_icon', 'name', )
    user_readonly_fields = ['name']
    user_readonly_inlines = []


class RouterInline(XOSTabularInline):
    model = Router.networks.through
    extra = 0
    verbose_name_plural = "Routers"
    verbose_name = "Router"
    suit_classes = 'suit-tab suit-tab-routers'


class NetworkParameterInline(PlStackGenericTabularInline):
    model = NetworkParameter
    extra = 0
    verbose_name_plural = "Parameters"
    verbose_name = "Parameter"
    suit_classes = 'suit-tab suit-tab-netparams'
    fields = ['backend_status_icon', 'parameter', 'value']
    readonly_fields = ('backend_status_icon', )


class NetworkPortInline(XOSTabularInline):
    fields = ['backend_status_icon', 'network', 'instance', 'ip', 'mac']
    readonly_fields = ("backend_status_icon", "ip", "mac")
    model = Port
    #selflink_fieldname = "instance"
    extra = 0
    verbose_name_plural = "Ports"
    verbose_name = "Port"
    suit_classes = 'suit-tab suit-tab-ports'


class NetworkSlicesInline(XOSTabularInline):
    model = NetworkSlice
    selflink_fieldname = "slice"
    extra = 0
    verbose_name_plural = "Slices"
    verbose_name = "Slice"
    suit_classes = 'suit-tab suit-tab-networkslices'
    fields = ['backend_status_icon', 'network', 'slice']
    readonly_fields = ('backend_status_icon', )


class ControllerNetworkInline(XOSTabularInline):
    model = ControllerNetwork
    extra = 0
    verbose_name_plural = "Controller Networks"
    verbose_name = "Controller Network"
    suit_classes = 'suit-tab suit-tab-admin-only'
    fields = ['backend_status_icon', 'controller',
              'net_id', 'subnet_id', 'subnet']
    readonly_fields = ('backend_status_icon', )


class NetworkForm(forms.ModelForm):

    class Meta:
        model = Network
        widgets = {
            'topologyParameters': UploadTextareaWidget,
            'controllerParameters': UploadTextareaWidget,
        }


class NetworkAdmin(XOSBaseAdmin):
    list_display = ("backend_status_icon", "name", "subnet", "ports", "labels")
    list_display_links = ('backend_status_icon', 'name', )
    readonly_fields = ("subnet", )
    inlines = [NetworkParameterInline, NetworkPortInline,
               NetworkSlicesInline, RouterInline]
    admin_inlines = [ControllerNetworkInline]

    form = NetworkForm

    fieldsets = [
        (None, {'fields': ['backend_status_text', 'name', 'template', 'ports', 'labels',
                           'owner', 'guaranteed_bandwidth', 'permit_all_slices',
                           'permitted_slices', 'network_id', 'router_id', 'subnet_id',
                           'subnet', 'autoconnect'],
                'classes':['suit-tab suit-tab-general']}),
        (None, {'fields': ['topology_parameters', 'controller_url', 'controller_parameters'],
                'classes':['suit-tab suit-tab-sdn']}),
    ]

    readonly_fields = ('backend_status_text', )
    user_readonly_fields = ['name', 'template', 'ports', 'labels', 'owner', 'guaranteed_bandwidth',
                            'permit_all_slices', 'permitted_slices', 'network_id', 'router_id',
                            'subnet_id', 'subnet', 'autoconnect']

    @property
    def suit_form_tabs(self):
        tabs = [('general', 'Network Details'),
                ('sdn', 'SDN Configuration'),
                ('netparams', 'Parameters'),
                ('ports', 'Ports'),
                ('networkslices', 'Slices'),
                ('routers', 'Routers'),
                ]

        request = getattr(_thread_locals, "request", None)
        if request and request.user.is_admin:
            tabs.append(('admin-only', 'Admin-Only'))

        return tabs


class NetworkTemplateAdmin(XOSBaseAdmin):
    list_display = ("backend_status_icon", "name",
                    "guaranteed_bandwidth", "visibility")
    list_display_links = ('backend_status_icon', 'name', )
    user_readonly_fields = ["name", "guaranteed_bandwidth", "visibility"]
    user_readonly_inlines = []
    inlines = [NetworkParameterInline, ]
    fieldsets = [
        (None, {'fields': ['name', 'description', 'guaranteed_bandwidth', 'visibility', 'translation', 'access', 'shared_network_name', 'shared_network_id', 'topology_kind', 'controller_kind'],
                'classes':['suit-tab suit-tab-general']}), ]
    suit_form_tabs = (('general', 'Network Template Details'),
                      ('netparams', 'Parameters'))


class PortAdmin(XOSBaseAdmin):
    list_display = ("backend_status_icon", "id", "ip")
    list_display_links = ('backend_status_icon', 'id')
    readonly_fields = ("subnet", )
    inlines = [NetworkParameterInline]

    fieldsets = [
        (None, {'fields': ['backend_status_text', 'network', 'instance', 'ip', 'port_id', 'mac'],
                'classes':['suit-tab suit-tab-general']}),
    ]

    readonly_fields = ('backend_status_text', )
    suit_form_tabs = (('general', 'Port Details'), ('netparams', 'Parameters'))


class FlavorAdmin(XOSBaseAdmin):
    list_display = ("backend_status_icon", "name",
                    "flavor", "order", "default")
    list_display_links = ("backend_status_icon", "name")
    user_readonly_fields = ("name", "flavor")
    fields = ("name", "description", "flavor", "order", "default")

# register a signal that caches the user's credentials when they log in


def cache_credentials(sender, user, request, **kwds):
    auth = {'username': request.POST['username'],
            'password': request.POST['password']}
    request.session['auth'] = auth
user_logged_in.connect(cache_credentials)


def dollar_field(fieldName, short_description):
    def newFunc(self, obj):
        try:
            x = "$ %0.2f" % float(getattr(obj, fieldName, 0.0))
        except:
            x = getattr(obj, fieldName, 0.0)
        return x
    newFunc.short_description = short_description
    return newFunc


def right_dollar_field(fieldName, short_description):
    def newFunc(self, obj):
        try:
            #x= '<div align=right style="width:6em">$ %0.2f</div>' % float(getattr(obj, fieldName, 0.0))
            x = '<div align=right>$ %0.2f</div>' % float(
                getattr(obj, fieldName, 0.0))
        except:
            x = getattr(obj, fieldName, 0.0)
        return x
    newFunc.short_description = short_description
    newFunc.allow_tags = True
    return newFunc


class InvoiceChargeInline(XOSTabularInline):
    model = Charge
    extra = 0
    verbose_name_plural = "Charges"
    verbose_name = "Charge"
    exclude = ['account']
    fields = ["date", "kind", "state", "object",
              "coreHours", "dollar_amount", "slice"]
    readonly_fields = ["date", "kind", "state",
                       "object", "coreHours", "dollar_amount", "slice"]
    can_delete = False
    max_num = 0

    dollar_amount = right_dollar_field("amount", "Amount")


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("date", "account")

    inlines = [InvoiceChargeInline]

    fields = ["date", "account", "dollar_amount"]
    readonly_fields = ["date", "account", "dollar_amount"]

    dollar_amount = dollar_field("amount", "Amount")


class InvoiceInline(XOSTabularInline):
    model = Invoice
    extra = 0
    verbose_name_plural = "Invoices"
    verbose_name = "Invoice"
    fields = ["date", "dollar_amount"]
    readonly_fields = ["date", "dollar_amount"]
    suit_classes = 'suit-tab suit-tab-accountinvoice'
    can_delete = False
    max_num = 0

    dollar_amount = right_dollar_field("amount", "Amount")


class PendingChargeInline(XOSTabularInline):
    model = Charge
    extra = 0
    verbose_name_plural = "Charges"
    verbose_name = "Charge"
    exclude = ["invoice"]
    fields = ["date", "kind", "state", "object",
              "coreHours", "dollar_amount", "slice"]
    readonly_fields = ["date", "kind", "state",
                       "object", "coreHours", "dollar_amount", "slice"]
    suit_classes = 'suit-tab suit-tab-accountpendingcharges'
    can_delete = False
    max_num = 0

    def queryset(self, request):
        qs = super(PendingChargeInline, self).queryset(request)
        qs = qs.filter(state="pending")
        return qs

    dollar_amount = right_dollar_field("amount", "Amount")


class PaymentInline(XOSTabularInline):
    model = Payment
    extra = 1
    verbose_name_plural = "Payments"
    verbose_name = "Payment"
    fields = ["date", "dollar_amount"]
    readonly_fields = ["date", "dollar_amount"]
    suit_classes = 'suit-tab suit-tab-accountpayments'
    can_delete = False
    max_num = 0

    dollar_amount = right_dollar_field("amount", "Amount")


class AccountAdmin(admin.ModelAdmin):
    list_display = ("site", "balance_due")

    inlines = [InvoiceInline, PaymentInline, PendingChargeInline]

    fieldsets = [
        (None, {'fields': ['site', 'dollar_balance_due', 'dollar_total_invoices', 'dollar_total_payments'], 'classes':['suit-tab suit-tab-general']}), ]

    readonly_fields = ['site', 'dollar_balance_due',
                       'dollar_total_invoices', 'dollar_total_payments']

    suit_form_tabs = (
        ('general', 'Account Details'),
        ('accountinvoice', 'Invoices'),
        ('accountpayments', 'Payments'),
        ('accountpendingcharges', 'Pending Charges'),
    )

    dollar_balance_due = dollar_field("balance_due", "Balance Due")
    dollar_total_invoices = dollar_field("total_invoices", "Total Invoices")
    dollar_total_payments = dollar_field("total_payments", "Total Payments")


class ProgramForm(forms.ModelForm):

    class Meta:
        model = Program
        widgets = {
            'contents': UploadTextareaWidget(attrs={'rows': 20, 'cols': 80, 'class': "input-xxlarge"}),
            'description': forms.Textarea(attrs={'rows': 3, 'cols': 80, 'class': 'input-xxlarge'}),
            'messages': forms.Textarea(attrs={'rows': 20, 'cols': 80, 'class': 'input-xxlarge'}),
            'output': forms.Textarea(attrs={'rows': 3, 'cols': 80, 'class': 'input-xxlarge'})
        }


class ProgramAdmin(XOSBaseAdmin):
    list_display = ("name", "status")
    list_display_links = ('name', "status")

    form = ProgramForm

    fieldsets = [
        (None, {'fields': ['name', 'command', 'kind', 'description', 'output', 'status'],
                'classes':['suit-tab suit-tab-general']}),
        (None, {'fields': ['contents'],
                'classes':['suit-tab suit-tab-contents']}),
        (None, {'fields': ['messages'],
                'classes':['suit-tab suit-tab-messages']}),
    ]

    readonly_fields = ("status",)

    @property
    def suit_form_tabs(self):
        tabs = [('general', 'Program Details'),
                ('contents', 'Program Source'),
                ('messages', 'Messages'),
                ]

        request = getattr(_thread_locals, "request", None)
        if request and request.user.is_admin:
            tabs.append(('admin-only', 'Admin-Only'))

        return tabs


class AddressPoolForm(forms.ModelForm):

    class Meta:
        model = Program
        widgets = {
            'addresses': UploadTextareaWidget(attrs={'rows': 20, 'cols': 80, 'class': "input-xxlarge"}),
        }


class AddressPoolAdmin(XOSBaseAdmin):
    list_display = ("name", "cidr")
    list_display_links = ('name',)

    form = AddressPoolForm

    fieldsets = [
        (None, {'fields': ['name', 'cidr', 'gateway_ip', 'gateway_mac', 'addresses', 'inuse', 'service'],
                'classes':['suit-tab suit-tab-general']}),
    ]

    readonly_fields = ("status",)

    @property
    def suit_form_tabs(self):
        tabs = [('general', 'Program Details'),
                ('contents', 'Program Source'),
                ('messages', 'Messages'),
                ]

#        request=getattr(_thread_locals, "request", None)
#        if request and request.user.is_admin:
#            tabs.append( ('admin-only', 'Admin-Only') )

        return tabs

class AddressPoolInline(XOSTabularInline):
    model = AddressPool
    extra = 0
    suit_classes = 'suit-tab suit-tab-addresspools'
    fields = ['cidr', 'gateway_ip', 'gateway_mac']
    readonly_fields = ['cidr',]

    # disable the add link
    def has_add_permission(self, request):
        return False

class DiagAdmin(XOSBaseAdmin):
    list_display = ("name", "backend_status", "backend_register")
    list_display_links = ('name',)

    fieldsets = [
        (None, {'fields': ['name', 'backend_status', 'backend_register'],
                'classes':['suit-tab suit-tab-general']}),
    ]

# Now register the new UserAdmin...
admin.site.register(User, UserAdmin)
# ... and, since we're not using Django's builtin permissions,
# unregister the Group model from admin.
# admin.site.unregister(Group)

# When debugging it is often easier to see all the classes, but for regular use
# only the top-levels should be displayed
showAll = False

admin.site.register(Deployment, DeploymentAdmin)
admin.site.register(Controller, ControllerAdmin)
admin.site.register(Site, SiteAdmin)
admin.site.register(Slice, SliceAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(ServiceController, ServiceControllerAdmin)
#admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Network, NetworkAdmin)
admin.site.register(Port, PortAdmin)
admin.site.register(Router, RouterAdmin)
admin.site.register(NetworkTemplate, NetworkTemplateAdmin)
admin.site.register(Program, ProgramAdmin)
#admin.site.register(Account, AccountAdmin)
#admin.site.register(Invoice, InvoiceAdmin)

if True:
    admin.site.register(NetworkParameterType, NetworkParameterTypeAdmin)
    admin.site.register(ServiceClass, ServiceClassAdmin)
    admin.site.register(Tag, TagAdmin)
    admin.site.register(ControllerRole)
    admin.site.register(SiteRole)
    admin.site.register(SliceRole)
    admin.site.register(Node, NodeAdmin)
    admin.site.register(NodeLabel, NodeLabelAdmin)
    #admin.site.register(SlicePrivilege, SlicePrivilegeAdmin)
    #admin.site.register(SitePrivilege, SitePrivilegeAdmin)
    admin.site.register(Instance, InstanceAdmin)
    admin.site.register(Image, ImageAdmin)
    admin.site.register(DashboardView, DashboardViewAdmin)
    admin.site.register(Flavor, FlavorAdmin)
    admin.site.register(TenantRoot, TenantRootAdmin)
    admin.site.register(TenantRootRole, TenantRootRoleAdmin)
    admin.site.register(TenantRole, TenantRoleAdmin)
    admin.site.register(TenantAttribute, TenantAttributeAdmin)
    admin.site.register(AddressPool, AddressPoolAdmin)
    admin.site.register(Diag, DiagAdmin)
