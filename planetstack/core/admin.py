from core.models import Site
from core.models import *
from openstack.manager import OpenStackManager

from django.contrib import admin
from django.contrib.auth.models import Group
from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.widgets import FilteredSelectMultiple, AdminTextareaWidget
from django.contrib.auth.forms import ReadOnlyPasswordHashField, AdminPasswordChangeForm
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone
from django.contrib.contenttypes import generic
from suit.widgets import LinkedSelect
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.html import conditional_escape, format_html
from django.forms.utils import flatatt, to_current_timezone
from cgi import escape as html_escape

import django_evolution
import threading

# thread locals necessary to work around a django-suit issue
_thread_locals = threading.local()

def backend_icon(obj): # backend_status, enacted, updated):
    #return "%s %s %s" % (str(obj.updated), str(obj.enacted), str(obj.backend_status))
    if (obj.enacted is not None) and obj.enacted >= obj.updated:
        return '<span style="min-width:16px;"><img src="/static/admin/img/icon_success.gif"></span>'
    else:
        if obj.backend_status == "Provisioning in progress" or obj.backend_status=="":
            return '<span style="min-width:16px;" title="%s"><img src="/static/admin/img/icon_clock.gif"></span>' % obj.backend_status
        else:
            return '<span style="min-width:16px;" title="%s"><img src="/static/admin/img/icon_error.gif"></span>' % html_escape(obj.backend_status, quote=True)

def backend_text(obj):
    icon = backend_icon(obj)
    if (obj.enacted is not None) and obj.enacted >= obj.updated:
        return "%s %s" % (icon, "successfully enacted")
    else:
        return "%s %s" % (icon, html_escape(obj.backend_status, quote=True))

class UploadTextareaWidget(AdminTextareaWidget):
    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        return format_html('<input type="file" style="width: 0; height: 0" id="btn_upload_%s" onChange="uploadTextarea(event,\'%s\');">' \
                           '<button onClick="$(\'#btn_upload_%s\').click(); return false;">Upload</button>' \
                           '<br><textarea{0}>\r\n{1}</textarea>' % (attrs["id"], attrs["id"], attrs["id"]),
                           flatatt(final_attrs),
                           force_text(value))

class PlainTextWidget(forms.HiddenInput):
    input_type = 'hidden'

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        return mark_safe(str(value) + super(PlainTextWidget, self).render(name, value, attrs))

class PermissionCheckingAdminMixin(object):
    # call save_by_user and delete_by_user instead of save and delete

    def has_add_permission(self, request, obj=None):
        return (not self.__user_is_readonly(request))

    def has_delete_permission(self, request, obj=None):
        return (not self.__user_is_readonly(request))

    def save_model(self, request, obj, form, change):
        if self.__user_is_readonly(request):
            # this 'if' might be redundant if save_by_user is implemented right
            raise PermissionDenied

        obj.caller = request.user
        # update openstack connection to use this site/tenant
        obj.save_by_user(request.user)

    def delete_model(self, request, obj):
        obj.delete_by_user(request.user)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
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

    def get_actions(self,request):
        actions = super(PermissionCheckingAdminMixin,self).get_actions(request)

        if self.__user_is_readonly(request):
            if 'delete_selected' in actions:
                del actions['delete_selected']

        return actions

    def change_view(self,request,object_id, extra_context=None):
        if self.__user_is_readonly(request):
            if not hasattr(self, "readonly_save"):
                # save the original readonly fields
                self.readonly_save = self.readonly_fields
                self.inlines_save = self.inlines
            if hasattr(self, "user_readonly_fields"):
                self.readonly_fields=self.user_readonly_fields
            if hasattr(self, "user_readonly_inlines"):
                self.inlines = self.user_readonly_inlines
        else:
            if hasattr(self, "readonly_save"):
                # restore the original readonly fields
                self.readonly_fields = self.readonly_save
            if hasattr(self, "inlines_save"):
                self.inlines = self.inlines_save

        try:
            return super(PermissionCheckingAdminMixin, self).change_view(request, object_id, extra_context=extra_context)
        except PermissionDenied:
            pass
        if request.method == 'POST':
            raise PermissionDenied
        request.readonly = True
        return super(PermissionCheckingAdminMixin, self).change_view(request, object_id, extra_context=extra_context)

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
        return super(PermissionCheckingAdminMixin, self).get_form(request, obj, **kwargs)

    def get_inline_instances(self, request, obj=None):
        inlines = super(PermissionCheckingAdminMixin, self).get_inline_instances(request, obj)

        # inlines that should only be shown to an admin user
        if request.user.is_admin:
            for inline_class in getattr(self, "admin_inlines", []):
                inlines.append(inline_class(self.model, self.admin_site))

        return inlines

class ReadOnlyAwareAdmin(PermissionCheckingAdminMixin, admin.ModelAdmin):
    # Note: Make sure PermissionCheckingAdminMixin is listed before
    # admin.ModelAdmin in the class declaration.

    pass

class PlanetStackBaseAdmin(ReadOnlyAwareAdmin):
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

class PlStackTabularInline(admin.TabularInline):
    def __init__(self, *args, **kwargs):
        super(PlStackTabularInline, self).__init__(*args, **kwargs)

        # InlineModelAdmin as no get_fields() method, so in order to add
        # the selflink field, we override __init__ to modify self.fields and
        # self.readonly_fields.

        self.setup_selflink()

    def get_change_url(self, model, id):
        """ Get the URL to a change form in the admin for this model """
        reverse_path = "admin:%s_change" % (model._meta.db_table)
        try:
            url = reverse(reverse_path, args=(id,))
        except NoReverseMatch:
            return None

        return url

    def setup_selflink(self):
        if hasattr(self, "selflink_fieldname"):
            """ self.selflink_model can be defined to punch through a relation
                to its target object. For example, in SliceNetworkInline, set
                selflink_model = "network", and the URL will lead to the Network
                object instead of trying to bring up a change view of the
                SliceNetwork object.
            """
            self.selflink_model = getattr(self.model,self.selflink_fieldname).field.rel.to
        else:
            self.selflink_model = self.model

        url = self.get_change_url(self.selflink_model, 0)

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
            url = self.get_change_url(self.selflink_model, obj.id)
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

class ReservationInline(PlStackTabularInline):
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

class NetworkLookerUpper:
    """ This is a callable that looks up a network name in a sliver and returns
        the ip address for that network.
    """

    byNetworkName = {}    # class variable

    def __init__(self, name):
        self.short_description = name
        self.__name__ = name
        self.network_name = name

    def __call__(self, obj):
        if obj is not None:
            for nbs in obj.networksliver_set.all():
                if (nbs.network.name == self.network_name):
                    return nbs.ip
        return ""

    def __str__(self):
        return self.network_name

    @staticmethod
    def get(network_name):
        """ We want to make sure we alwars return the same NetworkLookerUpper
            because sometimes django will cause them to be instantiated multiple
            times (and we don't want different ones in form.fields vs
            SliverInline.readonly_fields).
        """
        if network_name not in NetworkLookerUpper.byNetworkName:
            NetworkLookerUpper.byNetworkName[network_name] = NetworkLookerUpper(network_name)
        return NetworkLookerUpper.byNetworkName[network_name]

class SliverInline(PlStackTabularInline):
    model = Sliver
    fields = ['backend_status_icon', 'all_ips_string', 'instance_name', 'slice', 'controllerNetwork', 'flavor', 'image', 'node']
    extra = 0
    readonly_fields = ['backend_status_icon', 'all_ips_string', 'instance_name']
    suit_classes = 'suit-tab suit-tab-slivers'

    def queryset(self, request):
        return Sliver.select_by_user(request.user)

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'controllerNetwork':
           kwargs['queryset'] = Deployment.select_by_acl(request.user)
           kwargs['widget'] = forms.Select(attrs={'onChange': "sliver_deployment_changed(this);"})
        elif db_field.name == 'flavor':
           kwargs['widget'] = forms.Select(attrs={'onChange': "sliver_flavor_changed(this);"})

        field = super(SliverInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

        return field

class SiteInline(PlStackTabularInline):
    model = Site
    extra = 0
    suit_classes = 'suit-tab suit-tab-sites'

    def queryset(self, request):
        return Site.select_by_user(request.user)

class UserInline(PlStackTabularInline):
    model = User
    fields = ['backend_status_icon', 'email', 'firstname', 'lastname']
    readonly_fields = ('backend_status_icon', )
    extra = 0
    suit_classes = 'suit-tab suit-tab-users'

    def queryset(self, request):
        return User.select_by_user(request.user)

class SliceInline(PlStackTabularInline):
    model = Slice
    fields = ['backend_status_icon', 'name', 'site', 'serviceClass', 'service']
    readonly_fields = ('backend_status_icon', )
    extra = 0
    suit_classes = 'suit-tab suit-tab-slices'

    def queryset(self, request):
        return Slice.select_by_user(request.user)

class NodeInline(PlStackTabularInline):
    model = Node
    extra = 0
    suit_classes = 'suit-tab suit-tab-nodes'
    fields = ['backend_status_icon', 'name', 'site_deployment']
    readonly_fields = ('backend_status_icon', )

class DeploymentPrivilegeInline(PlStackTabularInline):
    model = DeploymentPrivilege
    extra = 0
    suit_classes = 'suit-tab suit-tab-admin-only'
    fields = ['backend_status_icon', 'user','role','deployment']
    readonly_fields = ('backend_status_icon', )

    def queryset(self, request):
        return DeploymentPrivilege.select_by_user(request.user)

class ControllerPrivilegeInline(PlStackTabularInline):
    model = ControllerPrivilege
    extra = 0
    suit_classes = 'suit-tab suit-tab-admin-only'
    fields = ['backend_status_icon', 'user','role','controller']
    readonly_fields = ('backend_status_icon', )

    def queryset(self, request):
        return ControllerPrivilege.select_by_user(request.user)

class ControllerSiteDeploymentsInline(PlStackTabularInline):
    model = ControllerSiteDeployments
    extra = 0
    suit_classes = 'suit-tab suit-tab-admin-only'
    fields = ['controller', 'site_deployment', 'tenant_id']

class SitePrivilegeInline(PlStackTabularInline):
    model = SitePrivilege
    extra = 0
    suit_classes = 'suit-tab suit-tab-siteprivileges'
    fields = ['backend_status_icon', 'user','site', 'role']
    readonly_fields = ('backend_status_icon', )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'site':
            kwargs['queryset'] = Site.select_by_user(request.user)

        if db_field.name == 'user':
            kwargs['queryset'] = User.select_by_user(request.user)
        return super(SitePrivilegeInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def queryset(self, request):
        return SitePrivilege.select_by_user(request.user)

class SiteDeploymentsInline(PlStackTabularInline):
    model = SiteDeployments
    extra = 0
    suit_classes = 'suit-tab suit-tab-deployments'
    fields = ['backend_status_icon', 'deployment','site', 'controller']
    readonly_fields = ('backend_status_icon', )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'site':
            kwargs['queryset'] = Site.select_by_user(request.user)

        if db_field.name == 'deployment':
            kwargs['queryset'] = Deployment.select_by_user(request.user)

        if db_field.name == 'controller':
            kwargs['queryset'] = Controller.select_by_user(request.user)

        return super(SiteDeploymentsInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def queryset(self, request):
        return SiteDeployments.select_by_user(request.user)


class SlicePrivilegeInline(PlStackTabularInline):
    model = SlicePrivilege
    suit_classes = 'suit-tab suit-tab-sliceprivileges'
    extra = 0
    fields = ('backend_status_icon', 'user', 'slice', 'role')
    readonly_fields = ('backend_status_icon', )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'slice':
           kwargs['queryset'] = Slice.select_by_user(request.user)
        if db_field.name == 'user':
           kwargs['queryset'] = User.select_by_user(request.user)

        return super(SlicePrivilegeInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def queryset(self, request):
        return SlicePrivilege.select_by_user(request.user)

class SliceNetworkInline(PlStackTabularInline):
    model = Network.slices.through
    selflink_fieldname = "network"
    extra = 0
    verbose_name = "Network Connection"
    verbose_name_plural = "Network Connections"
    suit_classes = 'suit-tab suit-tab-slicenetworks'
    fields = ['backend_status_icon', 'network']
    readonly_fields = ('backend_status_icon', )

class ImageDeploymentsInline(PlStackTabularInline):
    model = ImageDeployments
    extra = 0
    verbose_name = "Image Deployments"
    verbose_name_plural = "Image Deployments"
    suit_classes = 'suit-tab suit-tab-imagedeployments'
    fields = ['backend_status_icon', 'image', 'deployment']
    readonly_fields = ['backend_status_icon']

class ControllerImagesInline(PlStackTabularInline):
    model = ControllerImages
    extra = 0
    verbose_name = "Controller Images"
    verbose_name_plural = "Controller Images"
    suit_classes = 'suit-tab suit-tab-admin-only'
    fields = ['backend_status_icon', 'image', 'controller', 'glance_image_id']
    readonly_fields = ['backend_status_icon', 'glance_image_id']

class SliceRoleAdmin(PlanetStackBaseAdmin):
    model = SliceRole
    pass

class SiteRoleAdmin(PlanetStackBaseAdmin):
    model = SiteRole
    pass

class DeploymentAdminForm(forms.ModelForm):
    sites = forms.ModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        help_text="Select which sites are allowed to host nodes in this deployment",
        widget=FilteredSelectMultiple(
            verbose_name=('Sites'), is_stacked=False
        )
    )
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
        many_to_many = ["flavors",]

    def __init__(self, *args, **kwargs):
      request = kwargs.pop('request', None)
      super(DeploymentAdminForm, self).__init__(*args, **kwargs)

      self.fields['accessControl'].initial = "allow site " + request.user.site.name

      if self.instance and self.instance.pk:
        self.fields['sites'].initial = [x.site for x in self.instance.sitedeployments.all()]
        self.fields['images'].initial = [x.image for x in self.instance.imagedeployments.all()]
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
                #print "deleting site", sdp.site
                relation.delete()
            else:
                existing_dest_objs.append(getattr(relation, foreign_attrname))

        for dest_obj in selected_objs:
            if dest_obj not in existing_dest_objs:
                #print "adding site", site
                kwargs = {foreign_attrname: dest_obj, local_attrname: this_obj}
                relation = relation_class(**kwargs)
                relation.save()

    def save(self, commit=True):
      deployment = super(DeploymentAdminForm, self).save(commit=False)

      if commit:
        deployment.save()
        # this has to be done after save() if/when a deployment is first created
        deployment.flavors = self.cleaned_data['flavors']

      if deployment.pk:
        # save_m2m() doesn't seem to work with 'through' relations. So we
        #    create/destroy the through models ourselves. There has to be
        #    a better way...

        self.manipulate_m2m_objs(deployment, self.cleaned_data['sites'], deployment.sitedeployments.all(), SiteDeployments, "deployment", "site")
        self.manipulate_m2m_objs(deployment, self.cleaned_data['images'], deployment.imagedeployments.all(), ImageDeployments, "deployment", "image")
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

class SiteAssocInline(PlStackTabularInline):
    model = Site.deployments.through
    extra = 0
    suit_classes = 'suit-tab suit-tab-sites'

class DeploymentAdmin(PlanetStackBaseAdmin):
    model = Deployment
    fieldList = ['backend_status_text', 'name', 'sites', 'images', 'flavors', 'accessControl']
    fieldsets = [(None, {'fields': fieldList, 'classes':['suit-tab suit-tab-sites']})]
    # node no longer directly connected to deployment
    #inlines = [DeploymentPrivilegeInline,NodeInline,TagInline,ImageDeploymentsInline]
    inlines = [DeploymentPrivilegeInline,TagInline,ImageDeploymentsInline]
    list_display = ['backend_status_icon', 'name']
    list_display_links = ('backend_status_icon', 'name', )
    readonly_fields = ('backend_status_text', )

    user_readonly_fields = ['name']

    # nodes no longer direclty connected to deployments
    #suit_form_tabs =(('sites','Deployment Details'),('nodes','Nodes'),('deploymentprivileges','Privileges'),('tags','Tags'),('imagedeployments','Images'))
    suit_form_tabs =(('sites','Deployment Details'),('deploymentprivileges','Privileges'),('tags','Tags'),('imagedeployments','Images'))

    def get_form(self, request, obj=None, **kwargs):
        if request.user.isReadOnlyUser():
            kwargs["form"] = DeploymentAdminROForm
        else:
            kwargs["form"] = DeploymentAdminForm
        adminForm = super(DeploymentAdmin,self).get_form(request, obj, **kwargs)

        # from stackexchange: pass the request object into the form

        class AdminFormMetaClass(adminForm):
           def __new__(cls, *args, **kwargs):
               kwargs['request'] = request
               return adminForm(*args, **kwargs)

        return AdminFormMetaClass

class ControllerAdminForm(forms.ModelForm):
    site_deployments = forms.ModelMultipleChoiceField(
        queryset=SiteDeployments.objects.all(),
        required=False,
        help_text="Select which sites deployments are managed by this controller",
        widget=FilteredSelectMultiple(
            verbose_name=('Site Deployments'), is_stacked=False
        )
    )

    class Meta: 
        model = Controller
        
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super(ControllerAdminForm, self).__init__(*args, **kwargs)  

        if self.instance and self.instance.pk:
            self.fields['site_deployments'].initial = [x.site_deployment for x in self.instance.controllersitedeployments.all()]

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
                #print "deleting site", sdp.site
                relation.delete()
            else:
                existing_dest_objs.append(getattr(relation, foreign_attrname))

        for dest_obj in selected_objs:
            if dest_obj not in existing_dest_objs:
                #print "adding site", site
                kwargs = {foreign_attrname: dest_obj, local_attrname: this_obj}
                relation = relation_class(**kwargs)
                relation.save()

    def save(self, commit=True):
        controller = super(ControllerAdminForm, self).save(commit=False)
        if commit:
            controller.save()

        if controller.pk:
            # save_m2m() doesn't seem to work with 'through' relations. So we
            #    create/destroy the through models ourselves. There has to be
            #    a better way...
            self.manipulate_m2m_objs(controller, self.cleaned_data['site_deployments'], controller.controllersitedeployments.all(), ControllerSiteDeployments, "controller", "site_deployment")

        self.save_m2m()

        return controller 
      
class ControllerAdmin(PlanetStackBaseAdmin):
    model = Controller 
    fieldList = ['name', 'version', 'backend_type', 'auth_url', 'admin_user', 'admin_tenant','admin_password']
    #fieldsets = [(None, {'fields': fieldList, 'classes':['suit-tab suit-tab-general']})]
    inlines = [ControllerSiteDeploymentsInline] # ,ControllerImagesInline]
    list_display = ['backend_status_icon', 'name', 'version', 'backend_type']
    list_display_links = ('backend_status_icon', 'name', )
    readonly_fields = ('backend_status_text',)

    user_readonly_fields = []

    def get_form(self, request, obj=None, **kwargs):
        print self.fieldsets
        if request.user.isReadOnlyUser():
            kwargs["form"] = ControllerAdminROForm
        else:
            kwargs["form"] = ControllerAdminForm
        adminForm = super(ControllerAdmin,self).get_form(request, obj, **kwargs)

        # from stackexchange: pass the request object into the form

        class AdminFormMetaClass(adminForm):
           def __new__(cls, *args, **kwargs):
               kwargs['request'] = request
               return adminForm(*args, **kwargs)

        return AdminFormMetaClass

class ServiceAttrAsTabInline(PlStackTabularInline):
    model = ServiceAttribute
    fields = ['name','value']
    extra = 0
    suit_classes = 'suit-tab suit-tab-serviceattrs'

class ServiceAdmin(PlanetStackBaseAdmin):
    list_display = ("backend_status_icon","name","description","versionNumber","enabled","published")
    list_display_links = ('backend_status_icon', 'name', )
    fieldList = ["backend_status_text","name","description","versionNumber","enabled","published"]
    fieldsets = [(None, {'fields': fieldList, 'classes':['suit-tab suit-tab-general']})]
    inlines = [ServiceAttrAsTabInline,SliceInline]
    readonly_fields = ('backend_status_text', )

    user_readonly_fields = fieldList

    suit_form_tabs =(('general', 'Service Details'),
        ('slices','Slices'),
        ('serviceattrs','Additional Attributes'),
    )

class SiteAdmin(PlanetStackBaseAdmin):
    fieldList = ['backend_status_text', 'name', 'site_url', 'enabled', 'is_public', 'login_base', 'accountLink','location']
    fieldsets = [
        (None, {'fields': fieldList, 'classes':['suit-tab suit-tab-general']}),
        #('Deployment Networks', {'fields': ['deployments'], 'classes':['suit-tab suit-tab-deployments']}),
    ]
    suit_form_tabs =(('general', 'Site Details'),
        ('users','Users'),
        ('siteprivileges','Privileges'),
        ('deployments','Deployments'),
        ('slices','Slices'),
        #('nodes','Nodes'),
        ('tags','Tags'),
    )
    readonly_fields = ['backend_status_text', 'accountLink']

    user_readonly_fields = ['name', 'deployments','site_url', 'enabled', 'is_public', 'login_base', 'accountLink']

    list_display = ('backend_status_icon', 'name', 'login_base','site_url', 'enabled')
    list_display_links = ('backend_status_icon', 'name', )
    filter_horizontal = ('deployments',)
    inlines = [SliceInline,UserInline,TagInline, SitePrivilegeInline, SiteDeploymentsInline]
    search_fields = ['name']

    def queryset(self, request):
        return Site.select_by_user(request.user)

    def get_formsets(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            # hide MyInline in the add view
            if obj is None:
                continue
            if isinstance(inline, SliverInline):
                inline.model.caller = request.user
            yield inline.get_formset(request, obj)

    def accountLink(self, obj):
        link_obj = obj.accounts.all()
        if link_obj:
            reverse_path = "admin:core_account_change"
            url = reverse(reverse_path, args =(link_obj[0].id,))
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
        

class SitePrivilegeAdmin(PlanetStackBaseAdmin):
    fieldList = ['backend_status_text', 'user', 'site', 'role']
    fieldsets = [
        (None, {'fields': fieldList, 'classes':['collapse']})
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
                site_privileges = SitePrivilege.objects.filter(user=request.user).filter(role__in=roles)
                sites = [site_privilege.site for site_privilege in site_privileges]
                site_privileges = SitePrivilege.objects.filter(site__in=sites)
                emails = [site_privilege.user.email for site_privilege in site_privileges]
                users = User.objects.filter(email__in=emails)
                kwargs['queryset'] = users

        return super(SitePrivilegeAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def queryset(self, request):
        # admins can see all privileges. Users can only see privileges at sites
        # where they have the admin role or pi role.
        qs = super(SitePrivilegeAdmin, self).queryset(request)
        #if not request.user.is_admin:
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
        if (not isinstance(site,Site)):
            # previous code indicates 'site' could be a site_id and not a site?
            site = Slice.objects.get(id=site.id)
        if not name.startswith(site.login_base):
            raise forms.ValidationError('slice name must begin with %s' % site.login_base)
        return cleaned_data

class ControllerSlicesInline(PlStackTabularInline):
    model = ControllerSlices
    extra = 0
    verbose_name = "Controller Slices"
    verbose_name_plural = "Controller Slices"
    suit_classes = 'suit-tab suit-tab-admin-only'
    fields = ['backend_status_icon', 'controller', 'tenant_id']
    readonly_fields = ('backend_status_icon', )

class SliceAdmin(PlanetStackBaseAdmin):
    form = SliceForm
    fieldList = ['backend_status_text', 'site', 'name', 'serviceClass', 'enabled','description', 'service', 'slice_url', 'max_slivers']
    fieldsets = [('Slice Details', {'fields': fieldList, 'classes':['suit-tab suit-tab-general']}),]
    readonly_fields = ('backend_status_text', )
    list_display = ('backend_status_icon', 'name', 'site','serviceClass', 'slice_url', 'max_slivers')
    list_display_links = ('backend_status_icon', 'name', )
    inlines = [SlicePrivilegeInline,SliverInline, TagInline, ReservationInline,SliceNetworkInline]
    admin_inlines = [ControllerSlicesInline]

    user_readonly_fields = fieldList

    @property
    def suit_form_tabs(self):
        tabs =[('general', 'Slice Details'),
          ('slicenetworks','Networks'),
          ('sliceprivileges','Privileges'),
          ('slivers','Slivers'),
          ('tags','Tags'),
          ('reservations','Reservations'),
          ]

        request=getattr(_thread_locals, "request", None)
        if request and request.user.is_admin:
            tabs.append( ('admin-only', 'Admin-Only') )

        return tabs
    
    def add_view(self, request, form_url='', extra_context=None):
        # revert to default read-only fields
        self.readonly_fields = ('backend_status_text',)
        return super(SliceAdmin, self).add_view(request, form_url, extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        # cannot change the site of an existing slice so make the site field read only
        if object_id:
            self.readonly_fields = ('backend_status_text','site')
        return super(SliceAdmin, self).change_view(request, object_id, form_url)

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        deployment_nodes = []
        for node in Node.objects.all():
            deployment_nodes.append( (node.deployment.id, node.id, node.name) )

        deployment_flavors = []
        for flavor in Flavor.objects.all():
            for deployment in flavor.deployments.all():
                deployment_flavors.append( (deployment.id, flavor.id, flavor.name) )

        deployment_images = []
        for image in Image.objects.all():
            for deployment_image in image.imagedeployments.all():
                deployment_images.append( (deployment_image.controller.id, image.id, image.name) )

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
            kwargs['queryset'] = Site.select_by_user(request.user)
            kwargs['widget'] = forms.Select(attrs={'onChange': "update_slice_prefix(this, $($(this).closest('fieldset')[0]).find('.field-name input')[0].id)"})

        return super(SliceAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def queryset(self, request):
        # admins can see all keys. Users can only see slices they belong to.
        return Slice.select_by_user(request.user)

    def get_formsets(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            # hide MyInline in the add view
            if obj is None:
                continue
            if isinstance(inline, SliverInline):
                inline.model.caller = request.user
            yield inline.get_formset(request, obj)

class SlicePrivilegeAdmin(PlanetStackBaseAdmin):
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


class ImageAdmin(PlanetStackBaseAdmin):

    fieldsets = [('Image Details',
                   {'fields': ['backend_status_text', 'name', 'disk_format', 'container_format'],
                    'classes': ['suit-tab suit-tab-general']})
               ]
    readonly_fields = ('backend_status_text', )

    suit_form_tabs =(('general','Image Details'),('slivers','Slivers'),('imagedeployments','Deployments'), ('controllerimages', 'Controllers'))

    inlines = [SliverInline, ControllerImagesInline]

    user_readonly_fields = ['name', 'disk_format', 'container_format']

    list_display = ['backend_status_icon', 'name']
    list_display_links = ('backend_status_icon', 'name', )

class NodeForm(forms.ModelForm):
    class Meta:
        widgets = {
            'site': LinkedSelect,
            'deployment': LinkedSelect
        }

class NodeAdmin(PlanetStackBaseAdmin):
    form = NodeForm
    list_display = ('backend_status_icon', 'name', 'site_deployment')
    list_display_links = ('backend_status_icon', 'name', )
    list_filter = ('site_deployment',)

    inlines = [TagInline,SliverInline]
    fieldsets = [('Node Details', {'fields': ['backend_status_text', 'name','site_deployment'], 'classes':['suit-tab suit-tab-details']})]
    readonly_fields = ('backend_status_text', )

    user_readonly_fields = ['name','site_deployment']
    user_readonly_inlines = [TagInline,SliverInline]

    suit_form_tabs =(('details','Node Details'),('slivers','Slivers'),('tags','Tags'))


class SliverForm(forms.ModelForm):
    class Meta:
        model = Sliver
        ip = forms.CharField(widget=PlainTextWidget)
        instance_name = forms.CharField(widget=PlainTextWidget)
        widgets = {
            'ip': PlainTextWidget(),
            'instance_name': PlainTextWidget(),
            'slice': LinkedSelect,
            'controllerNetwork': LinkedSelect,
            'node': LinkedSelect,
            'image': LinkedSelect
        }

class TagAdmin(PlanetStackBaseAdmin):
    list_display = ['backend_status_icon', 'service', 'name', 'value', 'content_type', 'content_object',]
    list_display_links = list_display
    user_readonly_fields = ['service', 'name', 'value', 'content_type', 'content_object',]
    user_readonly_inlines = []

class SliverAdmin(PlanetStackBaseAdmin):
    form = SliverForm
    fieldsets = [
        ('Sliver Details', {'fields': ['backend_status_text', 'slice', 'controllerNetwork', 'node', 'ip', 'instance_name', 'flavor', 'image', ], 'classes': ['suit-tab suit-tab-general'], })
    ]
    readonly_fields = ('backend_status_text', )
    list_display = ['backend_status_icon', 'ip', 'instance_name', 'slice', 'flavor', 'image', 'node', 'controllerNetwork']
    list_display_links = ('backend_status_icon', 'ip',)

    suit_form_tabs =(('general', 'Sliver Details'),
        ('tags','Tags'),
    )

    inlines = [TagInline]

    user_readonly_fields = ['slice', 'controllerNetwork', 'node', 'ip', 'instance_name', 'flavor', 'image']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'slice':
            kwargs['queryset'] = Slice.select_by_user(request.user)

        return super(SliverAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def queryset(self, request):
        # admins can see all slivers. Users can only see slivers of
        # the slices they belong to.
        return Sliver.select_by_user(request.user)


    def get_formsets(self, request, obj=None):
        # make some fields read only if we are updating an existing record
        if obj == None:
            #self.readonly_fields = ('ip', 'instance_name')
            self.readonly_fields = ('backend_status_text',)
        else:
            self.readonly_fields = ('backend_status_text',)
            #self.readonly_fields = ('ip', 'instance_name', 'slice', 'image', 'key')

        for inline in self.get_inline_instances(request, obj):
            # hide MyInline in the add view
            if obj is None:
                continue
            if isinstance(inline, SliverInline):
                inline.model.caller = request.user
            yield inline.get_formset(request, obj)

    #def save_model(self, request, obj, form, change):
    #    # update openstack connection to use this site/tenant
    #    auth = request.session.get('auth', {})
    #    auth['tenant'] = obj.slice.name
    #    obj.os_manager = OpenStackManager(auth=auth, caller=request.user)
    #    obj.creator = request.user
    #    obj.save()

    #def delete_model(self, request, obj):
    #    # update openstack connection to use this site/tenant
    #    auth = request.session.get('auth', {})
    #    auth['tenant'] = obj.slice.name
    #    obj.os_manager = OpenStackManager(auth=auth, caller=request.user)
    #    obj.delete()

class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

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
        #user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField(label='Password',
                   help_text= '<a href=\"password/\">Change Password</a>.')

    class Meta:
        model = User
        widgets = { 'public_key': UploadTextareaWidget, }

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

class UserDashboardViewInline(PlStackTabularInline):
    model = UserDashboardView
    extra = 0
    suit_classes = 'suit-tab suit-tab-dashboards'
    fields = ['user', 'dashboardView', 'order']

class UserAdmin(PermissionCheckingAdminMixin, UserAdmin):
    # Note: Make sure PermissionCheckingAdminMixin is listed before
    # admin.ModelAdmin in the class declaration.

    class Meta:
        app_label = "core"

    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'firstname', 'lastname', 'site', 'last_login')
    list_filter = ('site',)
    inlines = [SlicePrivilegeInline,SitePrivilegeInline,ControllerPrivilegeInline,UserDashboardViewInline]

    fieldListLoginDetails = ['backend_status_text', 'email','site','password','is_active','is_readonly','is_admin','public_key']
    fieldListContactInfo = ['firstname','lastname','phone','timezone']

    fieldsets = (
        ('Login Details', {'fields': ['backend_status_text', 'email', 'site','password', 'is_active', 'is_readonly', 'is_admin', 'public_key'], 'classes':['suit-tab suit-tab-general']}),
        ('Contact Information', {'fields': ('firstname','lastname','phone', 'timezone'), 'classes':['suit-tab suit-tab-contact']}),
        #('Dashboard Views', {'fields': ('dashboards',), 'classes':['suit-tab suit-tab-dashboards']}),
        #('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'firstname', 'lastname', 'is_readonly', 'phone', 'public_key','password1', 'password2')},
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
            return (('general','Login Details'),
                         ('contact','Contact Information'),
                         ('sliceprivileges','Slice Privileges'),
                         ('siteprivileges','Site Privileges'),
                         ('controllerprivileges','Controller Privileges'),
                         ('dashboards','Dashboard Views'))

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'site':
            kwargs['queryset'] = Site.select_by_user(request.user)

        return super(UserAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def queryset(self, request):
        return User.select_by_user(request.user)

class DashboardViewAdmin(PlanetStackBaseAdmin):
    fieldsets = [('Dashboard View Details',
                   {'fields': ['backend_status_text', 'name', 'url'],
                    'classes': ['suit-tab suit-tab-general']})
               ]
    readonly_fields = ('backend_status_text', )

    suit_form_tabs =(('general','Dashboard View Details'),)

class ServiceResourceInline(PlStackTabularInline):
    model = ServiceResource
    extra = 0

class ServiceClassAdmin(PlanetStackBaseAdmin):
    list_display = ('backend_status_icon', 'name', 'commitment', 'membershipFee')
    list_display_links = ('backend_status_icon', 'name', )
    inlines = [ServiceResourceInline]

    user_readonly_fields = ['name', 'commitment', 'membershipFee']
    user_readonly_inlines = []

class ReservedResourceInline(PlStackTabularInline):
    model = ReservedResource
    extra = 0
    suit_classes = 'suit-tab suit-tab-reservedresources'

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        field = super(ReservedResourceInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

        if db_field.name == 'resource':
            # restrict resources to those that the slice's service class allows
            if request._slice is not None:
                field.queryset = field.queryset.filter(serviceClass = request._slice.serviceClass, calendarReservable=True)
                if len(field.queryset) > 0:
                    field.initial = field.queryset.all()[0]
            else:
                field.queryset = field.queryset.none()
        elif db_field.name == 'sliver':
            # restrict slivers to those that belong to the slice
            if request._slice is not None:
                field.queryset = field.queryset.filter(slice = request._slice)
            else:
                field.queryset = field.queryset.none()

        return field

    def queryset(self, request):
        return ReservedResource.select_by_user(request.user)

class ReservationChangeForm(forms.ModelForm):
    class Meta:
        model = Reservation
        widgets = {
            'slice' : LinkedSelect
        }

class ReservationAddForm(forms.ModelForm):
    slice = forms.ModelChoiceField(queryset=Slice.objects.all(), widget=forms.Select(attrs={"onChange":"document.getElementById('id_refresh').value=1; submit()"}))
    refresh = forms.CharField(widget=forms.HiddenInput())

    class Media:
       css = {'all': ('planetstack.css',)}   # .field-refresh { display: none; }

    def clean_slice(self):
        slice = self.cleaned_data.get("slice")
        x = ServiceResource.objects.filter(serviceClass = slice.serviceClass, calendarReservable=True)
        if len(x) == 0:
            raise forms.ValidationError("The slice you selected does not have a service class that allows reservations")
        return slice

    class Meta:
        model = Reservation
        widgets = {
            'slice' : LinkedSelect
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

class ReservationAdmin(PlanetStackBaseAdmin):
    fieldList = ['backend_status_text', 'slice', 'startTime', 'duration']
    fieldsets = [('Reservation Details', {'fields': fieldList, 'classes': ['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', )
    list_display = ('startTime', 'duration')
    form = ReservationAddForm

    suit_form_tabs = (('general','Reservation Details'), ('reservedresources','Reserved Resources'))

    inlines = [ReservedResourceInline]
    user_readonly_fields = fieldList

    def add_view(self, request, form_url='', extra_context=None):
        timezone.activate(request.user.timezone)
        request._refresh = False
        request._slice = None
        if request.method == 'POST':
            # "refresh" will be set to "1" if the form was submitted due to
            # a change in the Slice dropdown.
            if request.POST.get("refresh","1") == "1":
                request._refresh = True
                request.POST["refresh"] = "0"

            # Keep track of the slice that was selected, so the
            # reservedResource inline can filter items for the slice.
            request._slice = request.POST.get("slice",None)
            if (request._slice is not None):
                request._slice = Slice.objects.get(id=request._slice)

        result =  super(ReservationAdmin, self).add_view(request, form_url, extra_context)
        return result

    def changelist_view(self, request, extra_context = None):
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

class NetworkParameterTypeAdmin(PlanetStackBaseAdmin):
    list_display = ("backend_status_icon", "name", )
    list_display_links = ('backend_status_icon', 'name', )
    user_readonly_fields = ['name']
    user_readonly_inlines = []

class RouterAdmin(PlanetStackBaseAdmin):
    list_display = ("backend_status_icon", "name", )
    list_display_links = ('backend_status_icon', 'name', )
    user_readonly_fields = ['name']
    user_readonly_inlines = []

class RouterInline(PlStackTabularInline):
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

class NetworkSliversInline(PlStackTabularInline):
    fields = ['backend_status_icon', 'network','sliver','ip']
    readonly_fields = ("backend_status_icon", "ip", )
    model = NetworkSliver
    selflink_fieldname = "sliver"
    extra = 0
    verbose_name_plural = "Slivers"
    verbose_name = "Sliver"
    suit_classes = 'suit-tab suit-tab-networkslivers'

class NetworkSlicesInline(PlStackTabularInline):
    model = NetworkSlice
    selflink_fieldname = "slice"
    extra = 0
    verbose_name_plural = "Slices"
    verbose_name = "Slice"
    suit_classes = 'suit-tab suit-tab-networkslices'
    fields = ['backend_status_icon', 'network','slice']
    readonly_fields = ('backend_status_icon', )

class ControllerNetworksInline(PlStackTabularInline):
    model = ControllerNetworks
    extra = 0
    verbose_name_plural = "Controller Networks"
    verbose_name = "Controller Network"
    suit_classes = 'suit-tab suit-tab-admin-only'
    fields = ['backend_status_icon', 'controller','net_id','subnet_id']
    readonly_fields = ('backend_status_icon', )

class NetworkForm(forms.ModelForm):
    class Meta:
        model = Network
        widgets = {
            'topologyParameters': UploadTextareaWidget,
            'controllerParameters': UploadTextareaWidget,
        }

class NetworkAdmin(PlanetStackBaseAdmin):
    list_display = ("backend_status_icon", "name", "subnet", "ports", "labels")
    list_display_links = ('backend_status_icon', 'name', )
    readonly_fields = ("subnet", )

    inlines = [NetworkParameterInline, NetworkSliversInline, NetworkSlicesInline, RouterInline]
    admin_inlines = [ControllerNetworksInline]

    form=NetworkForm

    fieldsets = [
        (None, {'fields': ['backend_status_text', 'name','template','ports','labels','owner','guaranteedBandwidth', 'permitAllSlices','permittedSlices','network_id','router_id','subnet_id','subnet'],
                'classes':['suit-tab suit-tab-general']}),
        (None, {'fields': ['topologyParameters', 'controllerUrl', 'controllerParameters'],
                'classes':['suit-tab suit-tab-sdn']}),
                ]

    readonly_fields = ('backend_status_text', )
    user_readonly_fields = ['name','template','ports','labels','owner','guaranteedBandwidth', 'permitAllSlices','permittedSlices','network_id','router_id','subnet_id','subnet']

    @property
    def suit_form_tabs(self):
        tabs=[('general','Network Details'),
            ('sdn', 'SDN Configuration'),
            ('netparams', 'Parameters'),
            ('networkslivers','Slivers'),
            ('networkslices','Slices'),
            ('routers','Routers'),
        ]

        request=getattr(_thread_locals, "request", None)
        if request and request.user.is_admin:
            tabs.append( ('admin-only', 'Admin-Only') )

        return tabs


class NetworkTemplateAdmin(PlanetStackBaseAdmin):
    list_display = ("backend_status_icon", "name", "guaranteedBandwidth", "visibility")
    list_display_links = ('backend_status_icon', 'name', )
    user_readonly_fields = ["name", "guaranteedBandwidth", "visibility"]
    user_readonly_inlines = []
    fieldsets = [
        (None, {'fields': ['name', 'description', 'guaranteedBandwidth', 'visibility', 'translation', 'sharedNetworkName', 'sharedNetworkId', 'topologyKind', 'controllerKind'],
                'classes':['suit-tab suit-tab-general']}),]
    suit_form_tabs = (('general','Network Template Details'), )

class FlavorAdmin(PlanetStackBaseAdmin):
    list_display = ("backend_status_icon", "name", "flavor", "order", "default")
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
            x= "$ %0.2f" % float(getattr(obj, fieldName, 0.0))
        except:
            x=getattr(obj, fieldName, 0.0)
        return x
    newFunc.short_description = short_description
    return newFunc

def right_dollar_field(fieldName, short_description):
    def newFunc(self, obj):
        try:
            #x= '<div align=right style="width:6em">$ %0.2f</div>' % float(getattr(obj, fieldName, 0.0))
            x= '<div align=right>$ %0.2f</div>' % float(getattr(obj, fieldName, 0.0))
        except:
            x=getattr(obj, fieldName, 0.0)
        return x
    newFunc.short_description = short_description
    newFunc.allow_tags = True
    return newFunc

class InvoiceChargeInline(PlStackTabularInline):
    model = Charge
    extra = 0
    verbose_name_plural = "Charges"
    verbose_name = "Charge"
    exclude = ['account']
    fields = ["date", "kind", "state", "object", "coreHours", "dollar_amount", "slice"]
    readonly_fields = ["date", "kind", "state", "object", "coreHours", "dollar_amount", "slice"]
    can_delete = False
    max_num = 0

    dollar_amount = right_dollar_field("amount", "Amount")

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("date", "account")

    inlines = [InvoiceChargeInline]

    fields = ["date", "account", "dollar_amount"]
    readonly_fields = ["date", "account", "dollar_amount"]

    dollar_amount = dollar_field("amount", "Amount")

class InvoiceInline(PlStackTabularInline):
    model = Invoice
    extra = 0
    verbose_name_plural = "Invoices"
    verbose_name = "Invoice"
    fields = ["date", "dollar_amount"]
    readonly_fields = ["date", "dollar_amount"]
    suit_classes = 'suit-tab suit-tab-accountinvoice'
    can_delete=False
    max_num=0

    dollar_amount = right_dollar_field("amount", "Amount")

class PendingChargeInline(PlStackTabularInline):
    model = Charge
    extra = 0
    verbose_name_plural = "Charges"
    verbose_name = "Charge"
    exclude = ["invoice"]
    fields = ["date", "kind", "state", "object", "coreHours", "dollar_amount", "slice"]
    readonly_fields = ["date", "kind", "state", "object", "coreHours", "dollar_amount", "slice"]
    suit_classes = 'suit-tab suit-tab-accountpendingcharges'
    can_delete=False
    max_num=0

    def queryset(self, request):
        qs = super(PendingChargeInline, self).queryset(request)
        qs = qs.filter(state="pending")
        return qs

    dollar_amount = right_dollar_field("amount", "Amount")

class PaymentInline(PlStackTabularInline):
    model=Payment
    extra = 1
    verbose_name_plural = "Payments"
    verbose_name = "Payment"
    fields = ["date", "dollar_amount"]
    readonly_fields = ["date", "dollar_amount"]
    suit_classes = 'suit-tab suit-tab-accountpayments'
    can_delete=False
    max_num=0

    dollar_amount = right_dollar_field("amount", "Amount")

class AccountAdmin(admin.ModelAdmin):
    list_display = ("site", "balance_due")

    inlines = [InvoiceInline, PaymentInline, PendingChargeInline]

    fieldsets = [
        (None, {'fields': ['site', 'dollar_balance_due', 'dollar_total_invoices', 'dollar_total_payments'],'classes':['suit-tab suit-tab-general']}),]

    readonly_fields = ['site', 'dollar_balance_due', 'dollar_total_invoices', 'dollar_total_payments']

    suit_form_tabs =(
        ('general','Account Details'),
        ('accountinvoice', 'Invoices'),
        ('accountpayments', 'Payments'),
        ('accountpendingcharges','Pending Charges'),
    )

    dollar_balance_due = dollar_field("balance_due", "Balance Due")
    dollar_total_invoices = dollar_field("total_invoices", "Total Invoices")
    dollar_total_payments = dollar_field("total_payments", "Total Payments")

# Now register the new UserAdmin...
admin.site.register(User, UserAdmin)
# ... and, since we're not using Django's builtin permissions,
# unregister the Group model from admin.
#admin.site.unregister(Group)

#Do not show django evolution in the admin interface
from django_evolution.models import Version, Evolution
#admin.site.unregister(Version)
#admin.site.unregister(Evolution)


# When debugging it is often easier to see all the classes, but for regular use 
# only the top-levels should be displayed
showAll = False

admin.site.register(Deployment, DeploymentAdmin)
admin.site.register(Controller, ControllerAdmin)
admin.site.register(Site, SiteAdmin)
admin.site.register(Slice, SliceAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Network, NetworkAdmin)
admin.site.register(Router, RouterAdmin)
admin.site.register(NetworkTemplate, NetworkTemplateAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(Invoice, InvoiceAdmin)

if True:
    admin.site.register(NetworkParameterType, NetworkParameterTypeAdmin)
    admin.site.register(ServiceClass, ServiceClassAdmin)
    #admin.site.register(PlanetStack)
    admin.site.register(Tag, TagAdmin)
    admin.site.register(ControllerRole)
    admin.site.register(SiteRole)
    admin.site.register(SliceRole)
    admin.site.register(PlanetStackRole)
    admin.site.register(Node, NodeAdmin)
    #admin.site.register(SlicePrivilege, SlicePrivilegeAdmin)
    #admin.site.register(SitePrivilege, SitePrivilegeAdmin)
    admin.site.register(Sliver, SliverAdmin)
    admin.site.register(Image, ImageAdmin)
    admin.site.register(DashboardView, DashboardViewAdmin)
    admin.site.register(Flavor, FlavorAdmin)

