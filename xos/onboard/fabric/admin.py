from django.contrib import admin

from services.fabric.models import *
from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone
from django.contrib.contenttypes import generic
from suit.widgets import LinkedSelect
from core.models import AddressPool
from core.admin import ServiceAppAdmin,SliceInline,ServiceAttrAsTabInline, ReadOnlyAwareAdmin, XOSTabularInline, ServicePrivilegeInline, TenantRootTenantInline, TenantRootPrivilegeInline
from core.middleware import get_request

from functools import update_wrapper
from django.contrib.admin.views.main import ChangeList
from django.core.urlresolvers import reverse
from django.contrib.admin.utils import quote

class FabricServiceForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super (FabricServiceForm,self ).__init__(*args,**kwargs)

    def save(self, commit=True):
        return super(FabricServiceForm, self).save(commit=commit)

    class Meta:
        model = FabricService

class FabricServiceAdmin(ReadOnlyAwareAdmin):
    model = FabricService
    verbose_name = "Fabric Service"
    verbose_name_plural = "Fabric Services"
    list_display = ("backend_status_icon", "name", "enabled")
    list_display_links = ('backend_status_icon', 'name', )
    fieldsets = [(None, {'fields': ['backend_status_text', 'name','enabled','versionNumber', 'description', "view_url", "icon_url", "autoconfig", ],
                         'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', )
    inlines = [SliceInline,ServiceAttrAsTabInline,ServicePrivilegeInline]
    form = FabricServiceForm

    extracontext_registered_admins = True

    user_readonly_fields = ["name", "enabled", "versionNumber", "description"]

    suit_form_tabs =(('general', 'Fabric Service Details'),
        ('administration', 'Administration'),
        #('tools', 'Tools'),
        ('slices','Slices'),
        ('serviceattrs','Additional Attributes'),
        ('serviceprivileges','Privileges'),
    )

    suit_form_includes = (('fabricadmin.html', 'top', 'administration'),
                           )

    def queryset(self, request):
        return FabricService.get_service_objects_by_user(request.user)

admin.site.register(FabricService, FabricServiceAdmin)
