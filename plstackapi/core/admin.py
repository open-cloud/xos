from plstackapi.core.models import Site
from plstackapi.core.models import *
from plstackapi.openstack.manager import OpenStackManager
from plstackapi.openstack.driver import OpenStackDriver
from plstackapi.openstack.client import OpenStackClient

from django.contrib import admin
from django.contrib.auth.models import Group
from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.signals import user_logged_in 


class ReadonlyTabularInline(admin.TabularInline):
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

class SliverInline(admin.TabularInline):
    model = Sliver
    fields = ['ip', 'name', 'slice', 'numberCores', 'image', 'key', 'node', 'deploymentNetwork']
    extra = 0

class SiteInline(admin.TabularInline):
    model = Site
    extra = 0

class SliceInline(admin.TabularInline):
    model = Slice
    extra = 0

class UserInline(admin.TabularInline):
    model = PLUser
    extra = 0

class RoleInline(admin.TabularInline):
    model = Role
    extra = 0 

class NodeInline(admin.TabularInline):
    model = Node
    extra = 0

class PlainTextWidget(forms.Widget):
    def render(self, _name, value, attrs):
        return mark_safe(value) if value is not None else ''

class PlanetStackBaseAdmin(admin.ModelAdmin):
    save_on_top = False

class OSModelAdmin(PlanetStackBaseAdmin):
    """Attach client connection to openstack on delete() and save()"""

    def save_model(self, request, obj, form, change):
        auth = request.session.get('auth', {})
        auth['tenant'] = request.user.site.login_base
        obj.os_manager = OpenStackManager(auth=auth, caller=request.user)
        obj.save()

    def delete_model(self, request, obj):
        auth = request.session.get('auth', {})
        auth['tenant'] = request.user.site.login_base
        obj.os_manager = OpenStackManager(auth=auth, caller=request.user)
        obj.delete() 

class RoleAdmin(OSModelAdmin):
    fieldsets = [
        ('Role', {'fields': ['role_type']})
    ]
    list_display = ('role_type',)


class DeploymentNetworkAdminForm(forms.ModelForm):
    sites = forms.ModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name=('Sites'), is_stacked=False
        )
    )
    class Meta:
        model = DeploymentNetwork

    def __init__(self, *args, **kwargs):
        super(DeploymentNetworkAdminForm, self).__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['sites'].initial = self.instance.sites.all()

    def save(self, commit=True):
        deploymentNetwork = super(DeploymentNetworkAdminForm, self).save(commit=False)
        if commit:
            deploymentNetwork.save()

        if deploymentNetwork.pk:
            deploymentNetwork.sites = self.cleaned_data['sites']
            self.save_m2m()

        return deploymentNetwork

class DeploymentNetworkAdmin(PlanetStackBaseAdmin):
    form = DeploymentNetworkAdminForm
    inlines = [NodeInline,]

    def get_formsets(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            # hide MyInline in the add view
            if obj is None:
                continue
            # give inline object access to driver and caller
            client = OpenStackClient(tenant=request.user.site.login_base, **request.session.get('auth', {}))
            inline.model.driver = OpenStackDriver(client=client)
            inline.model.caller = request.user
            yield inline.get_formset(request, obj)

class SiteAdmin(OSModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'site_url', 'enabled', 'is_public', 'login_base']}),
        ('Location', {'fields': ['latitude', 'longitude']}),
        ('Deployment Networks', {'fields': ['deployments']})
    ]
    list_display = ('name', 'login_base','site_url', 'enabled')
    filter_horizontal = ('deployments',)
    inlines = [NodeInline,]
    search_fields = ['name']

    def get_formsets(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            # hide MyInline in the add view
            if obj is None:
                continue
            # give inline object access to driver and caller
            auth = request.session.get('auth', {})
            auth['tenant'] = request.user.site.login_base
            inline.model.os_manager = OpenStackManager(auth=auth, caller=request.user)
            yield inline.get_formset(request, obj)

class SitePrivilegeAdmin(PlanetStackBaseAdmin):
    fieldsets = [
        (None, {'fields': ['user', 'site', 'role']})
    ]
    list_display = ('user', 'site', 'role')

    def save_model(self, request, obj, form, change):
        # update openstack connection to use this site/tenant   
        auth = request.session.get('auth', {})
        auth['tenant'] = obj.site.login_base
        obj.os_manager = OpenStackManager(auth=auth, caller=request.user)
        obj.save()

    def delete_model(self, request, obj):
        # update openstack connection to use this site/tenant   
        auth = request.session.get('auth', {})
        auth['tenant'] = obj.site.login_base
        obj.os_manager = OpenStackManager(auth=auth, caller=request.user)
        obj.delete()

class KeyAdmin(OSModelAdmin):
    fieldsets = [
        ('Key', {'fields': ['name', 'key', 'type', 'blacklisted', 'user']})
    ]
    list_display = ['name', 'key', 'type', 'blacklisted', 'user']

    def get_queryset(self, request):
        # get keys user is allowed to see
        qs = super(KeyAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        # users can only see their own keys
        return qs.filter(user=request.user)  
        

class SliceAdmin(OSModelAdmin):
    fields = ['name', 'site', 'serviceClass', 'instantiation', 'description', 'slice_url']
    list_display = ('name', 'site','serviceClass', 'slice_url', 'instantiation')
    inlines = [SliverInline]

    def get_formsets(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            # hide MyInline in the add view
            if obj is None:
                continue
            # give inline object access to driver and caller
            auth = request.session.get('auth', {})
            auth['tenant'] = obj.name       # meed to connect using slice's tenant
            inline.model.os_manager = OpenStackManager(auth=auth, caller=request.user)
            yield inline.get_formset(request, obj)

    def get_queryset(self, request):
        qs = super(SliceAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        # users can only see slices at their site
        return qs.filter(site=request.user.site) 

class SliceMembershipAdmin(PlanetStackBaseAdmin):
    fieldsets = [
        (None, {'fields': ['user', 'slice', 'role']})
    ]
    list_display = ('user', 'slice', 'role')

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


class SubnetAdmin(PlanetStackBaseAdmin):
    fields = ['cidr', 'ip_version', 'start', 'end', 'slice']
    list_display = ('slice','cidr', 'start', 'end', 'ip_version')

    def save_model(self, request, obj, form, change):
        # update openstack connection to use this subnet's slice/tenant
        client = OpenStackClient(tenant=obj.slice.name, **request.session.get('auth', {}))
        obj.driver = OpenStackDriver(client=client)
        obj.caller = request.user
        obj.save()

    def delete_model(self, request, obj):
        # update openstack connection to use this subnet's slice/tenant
        client = OpenStackClient(tenant=obj.slice.name, **request.session.get('auth', {}))
        obj.driver = OpenStackDriver(client=client)
        obj.caller = request.user
        obj.delete()

class ImageAdmin(admin.ModelAdmin):
    fields = ['image_id', 'name', 'disk_format', 'container_format']

class NodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'site', 'deploymentNetwork')
    list_filter = ('deploymentNetwork',)


class SliverForm(forms.ModelForm):
    class Meta:
        ip = forms.CharField(widget=PlainTextWidget)
        model = Sliver
        widgets = {
            'ip': PlainTextWidget(),
        }

class SliverAdmin(PlanetStackBaseAdmin):
    form = SliverForm
    fieldsets = [
        ('Sliver', {'fields': ['ip', 'name', 'slice', 'numberCores', 'image', 'key', 'node', 'deploymentNetwork']})
    ]
    list_display = ['ip', 'name', 'slice', 'numberCores', 'image', 'key', 'node', 'deploymentNetwork']

    def save_model(self, request, obj, form, change):
        # update openstack connection to use this sliver's slice/tenant
        client = OpenStackClient(tenant=obj.slice.name, **request.session.get('auth', {}))
        obj.driver = OpenStackDriver(client=client)
        obj.caller = request.user
        obj.save()

    def delete_model(self, request, obj):
        # update openstack connection to use this sliver's slice/tenant
        client = OpenStackClient(tenant=obj.slice.name, **request.session.get('auth', {}))
        obj.driver = OpenStackDriver(client=client)
        obj.caller = request.user
        obj.delete()
     

class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = PLUser
        fields = ('email', 'firstname', 'lastname', 'phone', 'site')

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
        model = PLUser

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class PLUserAdmin(UserAdmin, OSModelAdmin):
    class Meta:
        app_label = "core"

    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'site', 'firstname', 'lastname', 'last_login')
    list_filter = ('site',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('firstname','lastname','phone','site')}),
        #('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'firstname', 'lastname', 'phone', 'site', 'password1', 'password2')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

# register a signal that caches the user's credentials when they log in
def cache_credentials(sender, user, request, **kwds):
    auth = {'username': request.POST['username'],
            'password': request.POST['password']}
    request.session['auth'] = auth
user_logged_in.connect(cache_credentials)

# Now register the new UserAdmin...
admin.site.register(PLUser, PLUserAdmin)
# ... and, since we're not using Django's builtin permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)

admin.site.register(Site, SiteAdmin)
admin.site.register(SitePrivilege, SitePrivilegeAdmin)
admin.site.register(Slice, SliceAdmin)
admin.site.register(SliceMembership, SliceMembershipAdmin)
admin.site.register(Subnet, SubnetAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Node, NodeAdmin)
admin.site.register(Sliver, SliverAdmin)
admin.site.register(Key, KeyAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(DeploymentNetwork, DeploymentNetworkAdmin)

