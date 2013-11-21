from core.models import Site
from core.models import *
from openstack.manager import OpenStackManager

from django.contrib import admin
from django.contrib.auth.models import Group
from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone
from django.contrib.contenttypes import generic
from suit.widgets import LinkedSelect

import django_evolution 

class SingletonAdmin (admin.ModelAdmin):
    def has_add_permission(self, request):
        num_objects = self.model.objects.count()
        if num_objects >= 1:
            return False
        else:
            return True


class PlStackTabularInline(admin.TabularInline):
    pass

class ReservationInline(PlStackTabularInline):
    model = Reservation
    extra = 0
    suit_classes = 'suit-tab suit-tab-reservations'


class ReadonlyTabularInline(PlStackTabularInline):
    can_delete = False
    extra = 0
    editable_fields = []

    def get_readonly_fields(self, request, obj=None):
        fields = []
        for field in self.model._meta.get_all_field_names():
            if (not field == 'id'):
                if (field not in self.editable_fields):
                    fields.append(field)
        return fields

    def has_add_permission(self, request):
        return False

class TagInline(generic.GenericTabularInline):
    model = Tag
    extra = 0
    suit_classes = 'suit-tab suit-tab-tags'

class NetworkLookerUpper:
    """ This is a callable that looks up a network name in a sliver and returns
        the ip address for that network.
    """

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

class SliverInline(PlStackTabularInline):
    model = Sliver
    fields = ['ip', 'instance_name', 'slice', 'numberCores', 'image', 'node', 'deploymentNetwork']
    extra = 0
    readonly_fields = ['ip', 'instance_name']
    suit_classes = 'suit-tab suit-tab-slivers'

# Note this is breaking in the admin.py when trying to use an inline to add a node/image 
#    def _declared_fieldsets(self):
#        # Return None so django will call get_fieldsets and we can insert our
#        # dynamic fields
#        return None
#
#    def get_readonly_fields(self, request, obj=None):
#        readonly_fields = super(SliverInline, self).get_readonly_fields(request, obj)
#
#        # Lookup the networks that are bound to the slivers, and add those
#        # network names to the list of readonly fields.
#
#        for sliver in obj.slivers.all():
#            for nbs in sliver.networksliver_set.all():
#                if nbs.ip:
#                    network_name = nbs.network.name
#                    if network_name not in [str(x) for x in readonly_fields]:
#                        readonly_fields.append(NetworkLookerUpper(network_name))
#
#        return readonly_fields
#
#    def get_fieldsets(self, request, obj=None):
#        form = self.get_formset(request, obj).form
#        # fields = the read/write files + the read-only fields
#        fields = self.fields
#        for fieldName in self.get_readonly_fields(request,obj):
#            if not fieldName in fields:
#                fields.append(fieldName)
#
#        return [(None, {'fields': fields})]

    

class SiteInline(PlStackTabularInline):
    model = Site
    extra = 0
    suit_classes = 'suit-tab suit-tab-sites'

class UserInline(PlStackTabularInline):
    model = User
    fields = ['email', 'firstname', 'lastname']
    extra = 0
    suit_classes = 'suit-tab suit-tab-users'

class SliceInline(PlStackTabularInline):
    model = Slice
    fields = ['name','site', 'serviceClass', 'service']
    extra = 0
    suit_classes = 'suit-tab suit-tab-slices'


class RoleInline(PlStackTabularInline):
    model = Role
    extra = 0 
    suit_classes = 'suit-tab suit-tab-roles'

class NodeInline(PlStackTabularInline):
    model = Node
    extra = 0
    suit_classes = 'suit-tab suit-tab-nodes'

class SlicePrivilegeInline(PlStackTabularInline):
    model = SlicePrivilege
    extra = 0
    suit_classes = 'suit-tab suit-tab-sliceprivileges'

class DeploymentPrivilegeInline(PlStackTabularInline):
    model = DeploymentPrivilege
    extra = 0
    suit_classes = 'suit-tab suit-tab-deploymentprivileges'

class SitePrivilegeInline(PlStackTabularInline):
    model = SitePrivilege
    extra = 0
    suit_classes = 'suit-tab suit-tab-siteprivileges'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'site':
            if not request.user.is_admin:
                # only show sites where user is an admin or pi
                roles = Role.objects.filter(role_type__in=['admin', 'pi'])
                site_privileges = SitePrivilege.objects.filter(user=request.user).filter(role__in=roles)
                login_bases = [site_privilege.site.login_base for site_privilege in site_privileges]
                sites = Site.objects.filter(login_base__in=login_bases)
                kwargs['queryset'] = sites

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
        return super(SitePrivilegeInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

class SitePrivilegeInline(PlStackTabularInline):
    model = SitePrivilege
    suit_classes = 'suit-tab suit-tab-siteprivileges'
    extra = 0
    fields = ('user', 'site','role')

class SlicePrivilegeInline(PlStackTabularInline):
    model = SlicePrivilege
    suit_classes = 'suit-tab suit-tab-sliceprivileges'
    extra = 0
    fields = ('user', 'slice','role')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'slice':
            if not request.user.is_admin:
                # only show slices at sites where caller has admin or pi role
                roles = Role.objects.filter(role_type__in=['admin', 'pi'])
                site_privileges = SitePrivilege.objects.filter(user=request.user).filter(role__in=roles)
                sites = [site_privilege.site for site_privilege in site_privileges]
                slices = Slice.objects.filter(site__in=sites)
                kwargs['queryset'] = slices 
        if db_field.name == 'user':
            if not request.user.is_admin:
                # only show users from sites where caller has admin or pi role
                roles = Role.objects.filter(role_type__in=['admin', 'pi'])
                site_privileges = SitePrivilege.objects.filter(user=request.user).filter(role__in=roles)
                sites = [site_privilege.site for site_privilege in site_privileges]
                site_privileges = SitePrivilege.objects.filter(site__in=sites)
                emails = [site_privilege.user.email for site_privilege in site_privileges]   
                users = User.objects.filter(email__in=emails) 
                kwargs['queryset'] = list(users)

        return super(SlicePrivilegeInline, self).formfield_for_foreignkey(db_field, request, **kwargs)

class SliceNetworkInline(PlStackTabularInline):
    model = Network.slices.through
    extra = 0
    verbose_name = "Network Connection"
    verbose_name_plural = "Network Connections"
    suit_classes = 'suit-tab suit-tab-slicenetworks'

class SliceTagInline(PlStackTabularInline):
    model = SliceTag
    extra = 0

class PlainTextWidget(forms.HiddenInput):
    input_type = 'hidden'

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        return mark_safe(str(value) + super(PlainTextWidget, self).render(name, value, attrs))

class PlanetStackBaseAdmin(admin.ModelAdmin):
    save_on_top = False

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
        widget=FilteredSelectMultiple(
            verbose_name=('Sites'), is_stacked=False
        )
    )
    class Meta:
        model = Deployment


class DeploymentAdmin(PlanetStackBaseAdmin):
    form = DeploymentAdminForm
    inlines = [DeploymentPrivilegeInline,NodeInline,TagInline]
    fieldsets = [
        (None, {'fields': ['sites'], 'classes':['suit-tab suit-tab-sites']}),]
    suit_form_tabs =(('sites', 'Sites'),('nodes','Nodes'),('deploymentprivileges','Privileges'),('tags','Tags'))

class ServiceAttrAsTabInline(PlStackTabularInline):
    model = ServiceAttribute
    fields = ['name','value']
    extra = 0
    suit_classes = 'suit-tab suit-tab-serviceattrs'

class ServiceAttributeInline(PlStackTabularInline):
    model = ServiceAttribute
    fields = ['name','value']
    extra = 0

class ServiceAdmin(PlanetStackBaseAdmin):
    list_display = ("name","enabled")
    fieldsets = [(None, {'fields': ['name','enabled','description']})]
    inlines = [ServiceAttributeInline,]

class SiteAdmin(PlanetStackBaseAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'site_url', 'enabled', 'is_public', 'login_base', 'location'], 'classes':['suit-tab suit-tab-general']}),
        ('Deployment Networks', {'fields': ['deployments'], 'classes':['suit-tab suit-tab-deployments']}),
    ]
    suit_form_tabs =(('general', 'Site Details'),
        ('users','Users'),
        ('siteprivileges','Privileges'),
        ('deployments','Deployments'),
        ('slices','Slices'),
        ('nodes','Nodes'), 
        ('tags','Tags'),
    )
    list_display = ('name', 'login_base','site_url', 'enabled')
    filter_horizontal = ('deployments',)
    inlines = [SliceInline,UserInline,TagInline, NodeInline, SitePrivilegeInline]
    search_fields = ['name']

    def queryset(self, request):
        # admins can see all keys. Users can only see sites they belong to.
        qs = super(SiteAdmin, self).queryset(request)
        if not request.user.is_admin:
            valid_sites = [request.user.site.login_base]
            roles = request.user.get_roles()
            for tenant_list in roles.values():
                valid_sites.extend(tenant_list)
            qs = qs.filter(login_base__in=valid_sites)
        return qs

    def get_formsets(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            # hide MyInline in the add view
            if obj is None:
                continue
            if isinstance(inline, SliceInline):
                inline.model.caller = request.user
            yield inline.get_formset(request, obj)

    def get_formsets(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            # hide MyInline in the add view
            if obj is None:
                continue
            if isinstance(inline, SliverInline):
                inline.model.caller = request.user
            yield inline.get_formset(request, obj)

class SitePrivilegeAdmin(PlanetStackBaseAdmin):
    fieldsets = [
        (None, {'fields': ['user', 'site', 'role'], 'classes':['collapse']})
    ]
    list_display = ('user', 'site', 'role')

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
        if not request.user.is_admin:
            roles = Role.objects.filter(role_type__in=['admin', 'pi'])
            site_privileges = SitePrivilege.objects.filter(user=request.user).filter(role__in=roles)
            login_bases = [site_privilege.site.login_base for site_privilege in site_privileges]
            sites = Site.objects.filter(login_base__in=login_bases)
            qs = qs.filter(site__in=sites)
        return qs

class SliceForm(forms.ModelForm):
    class Meta:
        model = Slice
        widgets = {
            'service': LinkedSelect 
        }

class SliceAdmin(PlanetStackBaseAdmin):
    form = SliceForm
    fieldsets = [('Slice Details', {'fields': ['name', 'site', 'serviceClass', 'enabled','description', 'service', 'slice_url'], 'classes':['suit-tab suit-tab-general']}),]
    list_display = ('name', 'site','serviceClass', 'slice_url')
    inlines = [SlicePrivilegeInline,SliverInline, TagInline, ReservationInline,SliceNetworkInline]


    #inlines = [SliverInline, SliceMembershipInline, TagInline, SliceTagInline, SliceNetworkInline]
    suit_form_tabs =(('general', 'Slice Details'),
        ('slicenetworks','Networks'),
        ('sliceprivileges','Privileges'),
        ('slivers','Slivers'),
        ('tags','Tags'),
        ('reservations','Reservations'),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'site':
            if not request.user.is_admin:
                # only show sites where user is a pi or admin 
                roles = Role.objects.filter(role_type__in=['admin', 'pi'])
                site_privileges = SitePrivilege.objects.filter(user=request.user).filter(role__in=roles)
                login_bases = [site_privilege.site.login_base for site_privilege in site_privileges]
                sites = Site.objects.filter(login_base__in=login_bases)
                kwargs['queryset'] = sites

        return super(SliceAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def queryset(self, request):
        # admins can see all keys. Users can only see slices they belong to.
        qs = super(SliceAdmin, self).queryset(request)
        if not request.user.is_admin:
            valid_slices = []
            roles = request.user.get_roles()
            for tenant_list in roles.values():
                valid_slices.extend(tenant_list)
            qs = qs.filter(name__in=valid_slices)
        return qs

    def get_formsets(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            # hide MyInline in the add view
            if obj is None:
                continue
            if isinstance(inline, SliverInline):
                inline.model.caller = request.user
            yield inline.get_formset(request, obj)

    def get_queryset(self, request):
        qs = super(SliceAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        # users can only see slices at their site
        return qs.filter(site=request.user.site)

    def save_model(self, request, obj, form, change):
        # update openstack connection to use this site/tenant
        obj.caller = request.user
        obj.save() 

class SlicePrivilegeAdmin(PlanetStackBaseAdmin):
    fieldsets = [
        (None, {'fields': ['user', 'slice', 'role']})
    ]
    list_display = ('user', 'slice', 'role')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'slice':
            if not request.user.is_admin:
                # only show slices at sites where caller has admin or pi role
                roles = Role.objects.filter(role_type__in=['admin', 'pi'])
                site_privileges = SitePrivilege.objects.filter(user=request.user).filter(role__in=roles)
                sites = [site_privilege.site for site_privilege in site_privileges]
                slices = Slice.objects.filter(site__in=sites)
                kwargs['queryset'] = slices
        
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

        return super(SlicePrivilegeAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def queryset(self, request):
        # admins can see all memberships. Users can only see memberships of
        # slices where they have the admin role.
        qs = super(SlicePrivilegeAdmin, self).queryset(request)
        if not request.user.is_admin:
            roles = Role.objects.filter(role_type__in=['admin', 'pi'])
            site_privileges = SitePrivilege.objects.filter(user=request.user).filter(role__in=roles)
            login_bases = [site_privilege.site.login_base for site_privilege in site_privileges]
            sites = Site.objects.filter(login_base__in=login_bases)
            slices = Slice.objects.filter(site__in=sites)
            qs = qs.filter(slice__in=slices)
        return qs

    def save_model(self, request, obj, form, change):
        # update openstack connection to use this site/tenant
        auth = request.session.get('auth', {})
        auth['tenant'] = obj.slice.name
        obj.os_manager = OpenStackManager(auth=auth, caller=request.user)
        obj.save()

    def delete_model(self, request, obj):
        # update openstack connection to use this site/tenant
        auth = request.session.get('auth', {})
        auth['tenant'] = obj.slice.name
        obj.os_manager = OpenStackManager(auth=auth, caller=request.user)
        obj.delete()


class ImageAdmin(PlanetStackBaseAdmin):

    fieldsets = [('Image Details', 
                   {'fields': ['image_id', 'name', 'disk_format', 'container_format'], 
                    'classes': ['suit-tab suit-tab-general']})
               ]

    suit_form_tabs =(('general','Image Details'),('slivers','Slivers'))

    inlines = [SliverInline]

class NodeForm(forms.ModelForm):
    class Meta:
        widgets = {
            'site': LinkedSelect,
            'deployment': LinkedSelect
        }

class NodeAdmin(admin.ModelAdmin):
    form = NodeForm
    list_display = ('name', 'site', 'deployment')
    list_filter = ('deployment',)
    inlines = [TagInline,SliverInline]
    fieldsets = [('Node Details', {'fields': ['name','site','deployment'], 'classes':['suit-tab suit-tab-details']})]

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
            'deploymentNetwork': LinkedSelect,
            'node': LinkedSelect,
            'image': LinkedSelect
        }

class TagAdmin(admin.ModelAdmin):
    list_display = ['service', 'name', 'value', 'content_type', 'content_object',]

class SliverAdmin(PlanetStackBaseAdmin):
    form = SliverForm
    fieldsets = [
        ('Sliver Details', {'fields': ['slice', 'deploymentNetwork', 'node', 'ip', 'instance_name', 'numberCores', 'image', ], 'classes': ['suit-tab suit-tab-general'], })
    ]
    list_display = ['ip', 'instance_name', 'slice', 'numberCores', 'image', 'node', 'deploymentNetwork']

    suit_form_tabs =(('general', 'Sliver Details'),
        ('tags','Tags'),
    )

    inlines = [TagInline]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'slice':
            if not request.user.is_admin:
                slices = set([sm.slice.name for sm in SlicePrivilege.objects.filter(user=request.user)]) 
                kwargs['queryset'] = Slice.objects.filter(name__in=list(slices))

        return super(SliverAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def queryset(self, request):
        # admins can see all slivers. Users can only see slivers of 
        # the slices they belong to.
        qs = super(SliverAdmin, self).queryset(request)
        if not request.user.is_admin:
            tenants = []
            roles = request.user.get_roles()
            for tenant_list in roles.values():
                tenants.extend(tenant_list)
            valid_slices = Slice.objects.filter(name__in=tenants)
            qs = qs.filter(slice__in=valid_slices)
        return qs

    def get_formsets(self, request, obj=None):
        # make some fields read only if we are updating an existing record
        if obj == None:
            #self.readonly_fields = ('ip', 'instance_name') 
            self.readonly_fields = () 
        else:
            self.readonly_fields = () 
            #self.readonly_fields = ('ip', 'instance_name', 'slice', 'image', 'key') 

        for inline in self.get_inline_instances(request, obj):
            # hide MyInline in the add view
            if obj is None:
                continue
            # give inline object access to driver and caller
            auth = request.session.get('auth', {})
            auth['tenant'] = obj.name       # meed to connect using slice's tenant
            inline.model.os_manager = OpenStackManager(auth=auth, caller=request.user)
            yield inline.get_formset(request, obj)

    def save_model(self, request, obj, form, change):
        # update openstack connection to use this site/tenant
        auth = request.session.get('auth', {})
        auth['tenant'] = obj.slice.name
        obj.os_manager = OpenStackManager(auth=auth, caller=request.user)
        obj.creator = request.user
        obj.save()

    def delete_model(self, request, obj):
        # update openstack connection to use this site/tenant
        auth = request.session.get('auth', {})
        auth['tenant'] = obj.slice.name
        obj.os_manager = OpenStackManager(auth=auth, caller=request.user)
        obj.delete()

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
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserAdmin(UserAdmin):
    class Meta:
        app_label = "core"

    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'firstname', 'lastname', 'is_admin', 'last_login')
    #list_display = ('email', 'username','firstname', 'lastname', 'is_admin', 'last_login')
    list_filter = ()
    inlines = [SlicePrivilegeInline,SitePrivilegeInline,DeploymentPrivilegeInline]
    fieldsets = (
        ('Login Details', {'fields': ('email', 'site','password', 'is_admin', 'public_key'), 'classes':['suit-tab suit-tab-general']}),
        ('Contact Information', {'fields': ('firstname','lastname','phone', 'timezone'), 'classes':['suit-tab suit-tab-contact']}),
        #('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'firstname', 'lastname', 'phone', 'public_key','password1', 'password2')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

    suit_form_tabs =(('general','Login Details'),('contact','Contact Information'),('sliceprivileges','Slice Privileges'),('siteprivileges','Site Privileges'),('deploymentprivileges','Deployment Privileges'))

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'site':
            if not request.user.is_admin:
                # show sites where caller is an admin or pi 
                sites = []
                for site_privilege in SitePrivilege.objects.filer(user=request.user):
                    if site_privilege.role.role_type in ['admin', 'pi']:
                        sites.append(site_privilege.site.login_base)  
                kwargs['queryset'] = Site.objects.filter(login_base__in(list(sites)))

        return super(UserAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

class ServiceResourceInline(admin.TabularInline):
    model = ServiceResource
    extra = 0

class ServiceClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'commitment', 'membershipFee')
    inlines = [ServiceResourceInline]

class ReservedResourceInline(admin.TabularInline):
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

class ReservationAdmin(admin.ModelAdmin):
    fieldsets = [('Reservation Details', {'fields': ['slice', 'startTime', 'duration'], 'classes': ['suit-tab suit-tab-general']})]
    list_display = ('startTime', 'duration')
    form = ReservationAddForm

    suit_form_tabs = (('general','Reservation Details'), ('reservedresources','Reserved Resources'))

    inlines = [ReservedResourceInline]

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

class NetworkParameterTypeAdmin(admin.ModelAdmin):
    list_display = ("name", )

class RouterAdmin(admin.ModelAdmin):
    list_display = ("name", )

class RouterInline(admin.TabularInline):
    model = Router.networks.through
    extra = 0
    verbose_name_plural = "Routers"
    verbose_name = "Router"
    suit_classes = 'suit-tab suit-tab-routers'

class NetworkParameterInline(generic.GenericTabularInline):
    model = NetworkParameter
    extra = 1
    verbose_name_plural = "Parameters"
    verbose_name = "Parameter"
    suit_classes = 'suit-tab suit-tab-netparams'

class NetworkSliversInline(admin.TabularInline):
    readonly_fields = ("ip", )
    model = NetworkSliver
    extra = 0
    verbose_name_plural = "Slivers"
    verbose_name = "Sliver"
    suit_classes = 'suit-tab suit-tab-networkslivers'

class NetworkSlicesInline(admin.TabularInline):
    model = NetworkSlice
    extra = 0
    verbose_name_plural = "Slices"
    verbose_name = "Slice"
    suit_classes = 'suit-tab suit-tab-networkslices'

class NetworkForm(forms.ModelForm):
    class Meta:
        widgets = {
            'deployment': LinkedSelect,
            'site': LinkedSelect,
        }

class NetworkAdmin(admin.ModelAdmin):
    form = NetworkForm
    list_display = ("name", "subnet", "ports", "labels")
    list_filter = ('deployment', )
    readonly_fields = ("subnet", )

    inlines = [NetworkParameterInline, NetworkSliversInline, NetworkSlicesInline, RouterInline]

    fieldsets = [
        (None, {'fields': ['name','template','ports','labels','owner','guaranteedBandwidth', 'permitAllSlices','permittedSlices','site','deployment','network_id','router_id','subnet_id','subnet'], 'classes':['suit-tab suit-tab-general']}),]

    suit_form_tabs =(
        ('general','Network Details'),
        ('netparams', 'Parameters'),
        ('networkslivers','Slivers'),
        ('networkslices','Slices'),
        ('routers','Routers'),
    )
class NetworkTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "guaranteedBandwidth", "visibility")

# register a signal that caches the user's credentials when they log in
def cache_credentials(sender, user, request, **kwds):
    auth = {'username': request.POST['username'],
            'password': request.POST['password']}
    request.session['auth'] = auth
user_logged_in.connect(cache_credentials)


# Now register the new UserAdmin...
admin.site.register(User, UserAdmin)
# ... and, since we're not using Django's builtin permissions,
# unregister the Group model from admin.
#admin.site.unregister(Group)

#Do not show django evolution in the admin interface
from django_evolution.models import Version, Evolution
admin.site.unregister(Version)
admin.site.unregister(Evolution)


# When debugging it is often easier to see all the classes, but for regular use 
# only the top-levels should be displayed
showAll = True

admin.site.register(Deployment, DeploymentAdmin)
admin.site.register(Site, SiteAdmin)
admin.site.register(Slice, SliceAdmin)
admin.site.register(ServiceClass, ServiceClassAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(Network, NetworkAdmin)
admin.site.register(Router, RouterAdmin)
admin.site.register(NetworkParameterType, NetworkParameterTypeAdmin)
admin.site.register(NetworkTemplate, NetworkTemplateAdmin)

if showAll:
    #admin.site.register(PlanetStack)
    admin.site.register(Tag, TagAdmin)
    admin.site.register(DeploymentRole)
    admin.site.register(SiteRole)
    admin.site.register(SliceRole)
    admin.site.register(PlanetStackRole)
    admin.site.register(Node, NodeAdmin)
    #admin.site.register(SlicePrivilege, SlicePrivilegeAdmin)
    #admin.site.register(SitePrivilege, SitePrivilegeAdmin)
    admin.site.register(Sliver, SliverAdmin)
    admin.site.register(Image, ImageAdmin)

