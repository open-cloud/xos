# admin.py - ExampleService Django Admin

from core.admin import ReadOnlyAwareAdmin, SliceInline
from core.middleware import get_request
from core.models import User

from django import forms
from django.contrib import admin

from services.exampleservice.models import *

class ExampleServiceForm(forms.ModelForm):

    class Meta:
        model = ExampleService

    def __init__(self, *args, **kwargs):
        super(ExampleServiceForm, self).__init__(*args, **kwargs)

        if self.instance:
            self.fields['service_message'].initial = self.instance.service_message

    def save(self, commit=True):
        self.instance.service_message = self.cleaned_data.get('service_message')
        return super(ExampleServiceForm, self).save(commit=commit)

class ExampleServiceAdmin(ReadOnlyAwareAdmin):

    model = ExampleService
    verbose_name = SERVICE_NAME_VERBOSE
    verbose_name_plural = SERVICE_NAME_VERBOSE_PLURAL
    form = ExampleServiceForm
    inlines = [SliceInline]

    list_display = ('backend_status_icon', 'name', 'service_message', 'enabled')
    list_display_links = ('backend_status_icon', 'name', 'service_message' )

    fieldsets = [(None, {
        'fields': ['backend_status_text', 'name', 'enabled', 'versionNumber', 'service_message', 'description',],
        'classes':['suit-tab suit-tab-general',],
        })]

    readonly_fields = ('backend_status_text', )
    user_readonly_fields = ['name', 'enabled', 'versionNumber', 'description',]

    extracontext_registered_admins = True

    suit_form_tabs = (
        ('general', 'Example Service Details', ),
        ('slices', 'Slices',),
        )

    suit_form_includes = ((
        'top',
        'administration'),
        )

    def queryset(self, request):
        return ExampleService.get_service_objects_by_user(request.user)

admin.site.register(ExampleService, ExampleServiceAdmin)

class ExampleTenantForm(forms.ModelForm):

    class Meta:
        model = ExampleTenant

    creator = forms.ModelChoiceField(queryset=User.objects.all())

    def __init__(self, *args, **kwargs):
        super(ExampleTenantForm, self).__init__(*args, **kwargs)

        self.fields['kind'].widget.attrs['readonly'] = True
        self.fields['kind'].initial = SERVICE_NAME

        self.fields['provider_service'].queryset = ExampleService.get_service_objects().all()

        if self.instance:
            self.fields['creator'].initial = self.instance.creator
            self.fields['tenant_message'].initial = self.instance.tenant_message

        if (not self.instance) or (not self.instance.pk):
            self.fields['creator'].initial = get_request().user
            if ExampleService.get_service_objects().exists():
                self.fields['provider_service'].initial = ExampleService.get_service_objects().all()[0]

    def save(self, commit=True):
        self.instance.creator = self.cleaned_data.get('creator')
        self.instance.tenant_message = self.cleaned_data.get('tenant_message')
        return super(ExampleTenantForm, self).save(commit=commit)


class ExampleTenantAdmin(ReadOnlyAwareAdmin):

    verbose_name = TENANT_NAME_VERBOSE
    verbose_name_plural = TENANT_NAME_VERBOSE_PLURAL

    list_display = ('id', 'backend_status_icon', 'instance', 'tenant_message')
    list_display_links = ('backend_status_icon', 'instance', 'tenant_message', 'id')

    fieldsets = [(None, {
        'fields': ['backend_status_text', 'kind', 'provider_service', 'instance', 'creator', 'tenant_message'],
        'classes': ['suit-tab suit-tab-general'],
        })]

    readonly_fields = ('backend_status_text', 'instance',)

    form = ExampleTenantForm

    suit_form_tabs = (('general', 'Details'),)

    def queryset(self, request):
        return ExampleTenant.get_tenant_objects_by_user(request.user)

admin.site.register(ExampleTenant, ExampleTenantAdmin)

