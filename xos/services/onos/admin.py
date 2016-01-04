from core.admin import (ReadOnlyAwareAdmin, ServiceAttrAsTabInline,
                        ServicePrivilegeInline, SliceInline,
                        TenantAttrAsTabInline)
from core.middleware import get_request
from core.models import User
from django import forms
from django.contrib import admin
from services.onos.models import ONOS_KIND, ONOSApp, ONOSService


class ONOSServiceForm(forms.ModelForm):
    use_external_host = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super(ONOSServiceForm, self).__init__(*args, **kwargs)
        if self.instance:
            # fields for the attributes
            self.fields[
                'use_external_host'].initial = self.instance.use_external_host

    def save(self, commit=True):
        self.instance.use_external_host = self.cleaned_data.get(
            "use_external_host")
        return super(ONOSServiceForm, self).save(commit=commit)

    class Meta:
        model = ONOSService


class ONOSServiceAdmin(ReadOnlyAwareAdmin):
    model = ONOSService
    verbose_name = "ONOS Service"
    verbose_name_plural = "ONOS Services"
    list_display = ("backend_status_icon", "name", "enabled")
    list_display_links = ('backend_status_icon', 'name', )
    fieldsets = [(None, {'fields': ['backend_status_text', 'name', 'enabled', 'versionNumber', 'description',
                                    "view_url", "icon_url", "use_external_host"], 'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', )
    inlines = [SliceInline, ServiceAttrAsTabInline, ServicePrivilegeInline]
    form = ONOSServiceForm

    extracontext_registered_admins = True

    user_readonly_fields = ["name", "enabled", "versionNumber", "description"]

    suit_form_tabs = (('general', 'ONOS Service Details'),
                      ('administration', 'Administration'),
                      ('slices', 'Slices'),
                      ('serviceattrs', 'Additional Attributes'),
                      ('serviceprivileges', 'Privileges'),
                      )

    suit_form_includes = (('onosadmin.html', 'top', 'administration'),
                          )

    def queryset(self, request):
        return ONOSService.get_service_objects_by_user(request.user)


class ONOSAppForm(forms.ModelForm):
    creator = forms.ModelChoiceField(queryset=User.objects.all())
    name = forms.CharField()
    dependencies = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super(ONOSAppForm, self).__init__(*args, **kwargs)
        self.fields['kind'].widget.attrs['readonly'] = True
        self.fields[
            'provider_service'].queryset = ONOSService.get_service_objects().all()
        if self.instance:
            # fields for the attributes
            self.fields['creator'].initial = self.instance.creator
            self.fields['name'].initial = self.instance.name
            self.fields['dependencies'].initial = self.instance.dependencies
        if (not self.instance) or (not self.instance.pk):
            # default fields for an 'add' form
            self.fields['kind'].initial = ONOS_KIND
            self.fields['creator'].initial = get_request().user
            if ONOSService.get_service_objects().exists():
                self.fields["provider_service"].initial = ONOSService.get_service_objects().all()[
                    0]

    def save(self, commit=True):
        self.instance.creator = self.cleaned_data.get("creator")
        self.instance.name = self.cleaned_data.get("name")
        self.instance.dependencies = self.cleaned_data.get("dependencies")
        return super(ONOSAppForm, self).save(commit=commit)

    class Meta:
        model = ONOSApp


class ONOSAppAdmin(ReadOnlyAwareAdmin):
    list_display = ('backend_status_icon', 'name', )
    list_display_links = ('backend_status_icon', 'name')
    fieldsets = [(None, {'fields': ['backend_status_text', 'kind', 'name', 'provider_service', 'subscriber_service', 'service_specific_attribute', "dependencies",
                                    'creator'],
                         'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', 'instance',
                       'service_specific_attribute')
    inlines = [TenantAttrAsTabInline]
    form = ONOSAppForm

    suit_form_tabs = (('general', 'Details'), ('tenantattrs', 'Attributes'))

    def queryset(self, request):
        return ONOSApp.get_tenant_objects_by_user(request.user)

admin.site.register(ONOSService, ONOSServiceAdmin)
admin.site.register(ONOSApp, ONOSAppAdmin)
