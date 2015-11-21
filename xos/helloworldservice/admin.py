
from core.admin import ReadOnlyAwareAdmin, ServiceAttrAsTabInline, ServicePrivilegeInline, SliceInline
from core.middleware import get_request
from core.models import User
from django import forms
from django.contrib import admin
from helloworldservice.models import HelloWorldService, HelloWorldTenant, HELLO_WORLD_KIND


class HelloWorldServiceAdmin(ReadOnlyAwareAdmin):
    model = HelloWorldService
    verbose_name = "Hello World Service"
    verbose_name_plural = "Hello World Services"
    list_display = ("backend_status_icon", "name", "enabled")
    list_display_links = ('backend_status_icon', 'name', )
    fieldsets = [(None, {'fields': ['backend_status_text', 'name', 'enabled',
                                    'versionNumber', 'description', "view_url"],
                         'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', )
    inlines = [SliceInline, ServiceAttrAsTabInline, ServicePrivilegeInline]

    extracontext_registered_admins = True

    user_readonly_fields = ["name", "enabled", "versionNumber", "description"]

    suit_form_tabs = (('general', 'Hello World Service Details'),
                      ('administration', 'Administration'),
                      ('slices', 'Slices'),
                      )

    suit_form_includes = (('helloworldserviceadmin.html',
                           'top',
                           'administration'),)

    def queryset(self, request):
        return HelloWorldService.get_service_objects_by_user(request.user)


class HelloWorldTenantForm(forms.ModelForm):
    creator = forms.ModelChoiceField(queryset=User.objects.all())
    display_message = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super(HelloWorldTenantForm, self).__init__(*args, **kwargs)
        self.fields['kind'].widget.attrs['readonly'] = True
        self.fields[
            'provider_service'].queryset = HelloWorldService.get_service_objects().all()
        if self.instance:
            self.fields['creator'].initial = self.instance.creator
            self.fields[
                'display_message'].initial = self.instance.display_message
        self.fields['kind'].initial = HELLO_WORLD_KIND
        if (not self.instance) or (not self.instance.pk):
            self.fields['creator'].initial = get_request().user
            if HelloWorldService.get_service_objects().exists():
                self.fields["provider_service"].initial = HelloWorldService.get_service_objects().all()[
                    0]

    def save(self, commit=True):
        self.instance.creator = self.cleaned_data.get("creator")
        self.instance.display_message = self.cleaned_data.get(
            "display_message")
        return super(HelloWorldTenantForm, self).save(commit=commit)

    class Meta:
        model = HelloWorldTenant


class HelloWorldTenantAdmin(ReadOnlyAwareAdmin):
    list_display = ('backend_status_icon', 'id', )
    list_display_links = ('backend_status_icon', 'id')
    fieldsets = [(None, {'fields': ['backend_status_text', 'kind',
                                    'provider_service', 'instance', 'creator',
                                    'display_message'],
                         'classes': ['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', 'instance',)
    form = HelloWorldTenantForm

    suit_form_tabs = (('general', 'Details'),)

    def queryset(self, request):
        return HelloWorldTenant.get_tenant_objects_by_user(request.user)

admin.site.register(HelloWorldService, HelloWorldServiceAdmin)
admin.site.register(HelloWorldTenant, HelloWorldTenantAdmin)
