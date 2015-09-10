from django.contrib import admin

from ceilometer.models import *
from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone
from django.contrib.contenttypes import generic
from suit.widgets import LinkedSelect
from core.admin import ServiceAppAdmin,SliceInline,ServiceAttrAsTabInline, ReadOnlyAwareAdmin, XOSTabularInline, ServicePrivilegeInline, TenantRootTenantInline, TenantRootPrivilegeInline

from functools import update_wrapper
from django.contrib.admin.views.main import ChangeList
from django.core.urlresolvers import reverse
from django.contrib.admin.utils import quote

class CeilometerServiceAdmin(ReadOnlyAwareAdmin):
    model = CeilometerService
    verbose_name = "Ceilometer Service"
    verbose_name_plural = "Ceilometer Service"
    list_display = ("backend_status_icon", "name", "enabled")
    list_display_links = ('backend_status_icon', 'name', )
    fieldsets = [(None, {'fields': ['backend_status_text', 'name','enabled','versionNumber', 'description',"view_url","icon_url" ], 'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', )
    inlines = [SliceInline,ServiceAttrAsTabInline,ServicePrivilegeInline]

    extracontext_registered_admins = True

    user_readonly_fields = ["name", "enabled", "versionNumber", "description"]

    suit_form_tabs =(('general', 'Ceilometer Service Details'),
        ('administration', 'Administration'),
        ('slices','Slices'),
        ('serviceattrs','Additional Attributes'),
        ('serviceprivileges','Privileges'),
    )

    suit_form_includes = (('ceilometeradmin.html', 'top', 'administration'),
                           )

    def queryset(self, request):
        return CeilometerService.get_service_objects_by_user(request.user)

class MonitoringChannelForm(forms.ModelForm):
    creator = forms.ModelChoiceField(queryset=User.objects.all())

    def __init__(self,*args,**kwargs):
        super (MonitoringChannelForm,self ).__init__(*args,**kwargs)
        self.fields['kind'].widget.attrs['readonly'] = True
        self.fields['provider_service'].queryset = CeilometerService.get_service_objects().all()
        if self.instance:
            # fields for the attributes
            self.fields['creator'].initial = self.instance.creator
        if (not self.instance) or (not self.instance.pk):
            # default fields for an 'add' form
            self.fields['kind'].initial = CEILOMETER_KIND
            if CeilometerService.get_service_objects().exists():
               self.fields["provider_service"].initial = CeilometerService.get_service_objects().all()[0]


    def save(self, commit=True):
        self.instance.creator = self.cleaned_data.get("creator")
        return super(MonitoringChannelForm, self).save(commit=commit)

    class Meta:
        model = MonitoringChannel

class MonitoringChannelAdmin(ReadOnlyAwareAdmin):
    list_display = ('backend_status_icon', 'id', )
    list_display_links = ('backend_status_icon', 'id')
    fieldsets = [ (None, {'fields': ['backend_status_text', 'kind', 'provider_service', 'service_specific_attribute',
                                     'sliver',
                                     'creator'],
                          'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', 'sliver', 'service_specific_attribute')
    form = MonitoringChannelForm

    suit_form_tabs = (('general','Details'),)

    def queryset(self, request):
        return MonitoringChannel.get_tenant_objects_by_user(request.user)

admin.site.register(CeilometerService, CeilometerServiceAdmin)
admin.site.register(MonitoringChannel, MonitoringChannelAdmin)

