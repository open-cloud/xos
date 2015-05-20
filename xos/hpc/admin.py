from django.contrib import admin

from hpc.models import *
from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone
from django.contrib.contenttypes import generic
from suit.widgets import LinkedSelect
from core.admin import ServiceAppAdmin,SliceInline,ServiceAttrAsTabInline, ReadOnlyAwareAdmin, XOSTabularInline, SliderWidget, ServicePrivilegeInline
from core.middleware import get_request

from functools import update_wrapper
from django.contrib.admin.views.main import ChangeList
from django.core.urlresolvers import reverse
from django.contrib.admin.utils import quote

import threading
_thread_locals = threading.local()

class FilteredChangeList(ChangeList):
    """ A special ChangeList with a doctored url_for_result function that
        points to the filteredchange view instead of the default change
        view.
    """

    def __init__(self, request, *args, **kwargs):
        self.hpcService = getattr(request, "hpcService", None)
        self.embedded = getattr(request, "embedded", False)
        super(FilteredChangeList, self).__init__(request, *args, **kwargs)

    def url_for_result(self, result):
        if (self.hpcService is None):
             return super(FilteredChangeList, self).url_for_result(result)

        pk = getattr(result, self.pk_attname)
        if self.embedded:
            return reverse('admin:%s_%s_embeddedfilteredchange' % (self.opts.app_label,
                                                           self.opts.model_name),
                           args=(quote(self.hpcService.id), quote(pk),),
                           current_app=self.model_admin.admin_site.name)

        else:
            return reverse('admin:%s_%s_filteredchange' % (self.opts.app_label,
                                                           self.opts.model_name),
                           args=(quote(self.hpcService.id), quote(pk),),
                           current_app=self.model_admin.admin_site.name)

class FilteredAdmin(ReadOnlyAwareAdmin):
   """
      One approach to filtering the HPC Admin views by HPCService. Encode
      the HPCService into the URL for the changelist view. Then we could do our
      custom filtering in self.filtered_changelist_view.

      To make this work, a few changes needed to be made to the change and
      change_list templates.

      1) "custom_changelist_breadcrumb_url" is used to replace the breadcrumb
         in change and add views with one that will point back to the filtered
         list.

      2) "custom_add_url" is used to replace the Add button's URL with one
         that points to the filtered add view.

      TODO: Save & Add Another,
            the add link when the changelist is empty
   """

   @property
   def change_list_template(self):
       return _thread_locals.change_list_template

   @property
   def change_form_template(self):
       return _thread_locals.change_form_template

   def get_urls(self):
       from django.conf.urls import patterns, url

       def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

       urls = super(FilteredAdmin, self).get_urls()
       info = self.model._meta.app_label, self.model._meta.model_name
       my_urls = [
           url(r'^(.+)/filteredlist/$', wrap(self.filtered_changelist_view), name="%s_%s_filteredchangelist" % info),
           url(r'^(.+)/embeddedfilteredlist/$', wrap(self.embedded_filtered_changelist_view), name="%s_%s_embeddedfilteredchangelist" % info),
           url(r'^(.+)/(.+)/filteredchange$', wrap(self.filtered_change_view), name='%s_%s_filteredchange' % info),
           url(r'^(.+)/(.+)/embeddedfilteredchange$', wrap(self.embedded_filtered_change_view), name='%s_%s_embeddedfilteredchange' % info),
           url(r'^(.+)/filteredadd/$', wrap(self.filtered_add_view), name='%s_%s_filteredadd' % info),
           url(r'^(.+)/embeddedfilteredadd/$', wrap(self.embedded_filtered_add_view), name='%s_%s_embeddedfilteredadd' % info),
       ]
       return my_urls + urls

   def add_extra_context(self, request, extra_context):
       super(FilteredAdmin, self).add_extra_context(request, extra_context)

       if getattr(request,"hpcService",None) is not None:
            extra_context["custom_changelist_breadcrumb_url"] = "/admin/hpc/%s/%s/filteredlist/" % (self.model._meta.model_name, str(request.hpcService.id))
            if getattr(request,"embedded",False):
                extra_context["custom_add_url"] = "/admin/hpc/%s/%s/embeddedfilteredadd/" % (self.model._meta.model_name, str(request.hpcService.id))
            else:
                extra_context["custom_add_url"] = "/admin/hpc/%s/%s/filteredadd/" % (self.model._meta.model_name, str(request.hpcService.id))

   def changelist_view(self, *args, **kwargs):
       if "template" in kwargs:
           _thread_locals.change_list_template = kwargs["template"]
           del kwargs["template"]
       else:
           _thread_locals.change_list_template = "admin/change_list_bc.html"
       return super(FilteredAdmin, self).changelist_view(*args, **kwargs)

   def filtered_changelist_view(self, request, hpcServiceId, extra_context=None):
       request.hpcService = HpcService.objects.get(id=hpcServiceId)
       return self.changelist_view(request, extra_context=extra_context)

   def embedded_filtered_changelist_view(self, request, hpcServiceId, extra_context=None):
       request.hpcService = HpcService.objects.get(id=hpcServiceId)
       request.embedded = True
       return self.changelist_view(request, template="admin/change_list_embedded.html", extra_context=extra_context)

   def change_view(self, *args, **kwargs):
       if "template" in kwargs:
           _thread_locals.change_form_template = kwargs["template"]
           del kwargs["template"]
       else:
           _thread_locals.change_form_template = "admin/change_form_bc.html"
       return super(FilteredAdmin, self).change_view(*args, **kwargs)

   def filtered_change_view(self, request, hpcServiceId, object_id, extra_context=None):
       request.hpcService = HpcService.objects.get(id=hpcServiceId)
       return self.change_view(request, object_id, extra_context=extra_context)

   def embedded_filtered_change_view(self, request, hpcServiceId, object_id, extra_context=None):
       request.hpcService = HpcService.objects.get(id=hpcServiceId)
       request.embedded = True
       return self.change_view(request, object_id, template="admin/change_form_embedded.html", extra_context=extra_context)

   def add_view(self, *args, **kwargs):
       if "template" in kwargs:
           _thread_locals.change_form_template = kwargs["template"]
           del kwargs["template"]
       else:
           _thread_locals.change_form_template = "admin/change_form_bc.html"
       return super(FilteredAdmin, self).add_view(*args, **kwargs)

   def filtered_add_view(self, request, hpcServiceId, extra_context=None):
       request.hpcService = HpcService.objects.get(id=hpcServiceId)
       return self.add_view(request, extra_context=extra_context)

   def embedded_filtered_add_view(self, request, hpcServiceId, extra_context=None):
       request.hpcService = HpcService.objects.get(id=hpcServiceId)
       request.embedded = True
       return self.add_view(request, template="admin/change_form_embedded.html", extra_context=extra_context)

   def get_queryset(self, request):
       # request.hpcService will be set in filtered_changelist_view so we can
       # use it to filter what will be displayed in the list.
       qs = self.model.objects.all()
       if (getattr(request,"hpcService",None) is not None) and (hasattr(self.model, "filter_by_hpcService")):
           qs = self.model.filter_by_hpcService(qs, request.hpcService)
       return qs

   def get_changelist(self, request, **kwargs):
       # We implement a custom ChangeList, so the URLs point to the
       # filtered_change_view rather than the default change_view.
       return FilteredChangeList

class HpcServiceForm(forms.ModelForm):
    scale = forms.IntegerField(widget = SliderWidget, required=False)

    def __init__(self, *args, **kwargs):
        super(HpcServiceForm, self).__init__(*args, **kwargs)
        self.fields['scale'].initial = kwargs["instance"].scale

    def save(self, *args, **kwargs):
        if self.cleaned_data['scale']:
             self.instance.scale = self.cleaned_data['scale']

        return super(HpcServiceForm, self).save(*args, **kwargs)


class HpcServiceAdmin(ReadOnlyAwareAdmin):
    model = HpcService
    verbose_name = "HPC Service"
    verbose_name_plural = "HPC Service"
    list_display = ("backend_status_icon", "name","enabled")
    list_display_links = ('backend_status_icon', 'name', )
    fieldsets = [(None, {'fields': ['backend_status_text', 'name','scale','enabled','versionNumber', 'description', "cmi_hostname", "hpc_port80", "watcher_hpc_network", "watcher_dnsredir_network", "watcher_dnsdemux_network"], 'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', )
    inlines = [SliceInline,ServiceAttrAsTabInline,ServicePrivilegeInline]
    form = HpcServiceForm

    extracontext_registered_admins = True

    user_readonly_fields = ["name", "enabled", "versionNumber", "description"]

    suit_form_tabs =(('general', 'HPC Service Details'),
        ('administration', 'Administration'),
        ('tools', 'Tools'),
        ('slices','Slices'),
        ('serviceattrs','Additional Attributes'),
                ('serviceprivileges','Privileges'),
    )

    suit_form_includes = (('hpcadmin.html', 'top', 'administration'),
                          ('hpctools.html', 'top', 'tools') )

    def url_for_model_changelist(self, request, model):
       if not request.resolver_match.args:
           return reverse('admin:%s_%s_changelist' % (model._meta.app_label, model._meta.model_name), current_app=model._meta.app_label)
       else:
           obj_id = request.resolver_match.args[0]
           changelist_url = reverse('admin:%s_%s_filteredchangelist' % (model._meta.app_label, model._meta.model_name), args=(obj_id,), current_app=model._meta.app_label)
           return changelist_url

class HPCAdmin(FilteredAdmin):
   # Change the application breadcrumb to point to an HPC Service if one is
   # defined

   """
   @property
   def change_form_template(self):
       request=get_request()
       if request.GET.get("embedded",False):
           return "admin/change_form_embedded.html"
       else:
           return "admin/change_form_bc.html"
   """

   #change_form_template = "admin/change_form_bc.html"
   #change_list_template = "admin/change_list_bc.html"
   custom_app_breadcrumb_name = "Hpc"
   @property
   def custom_app_breadcrumb_url(self):
       services = HpcService.objects.all()
       if len(services)==1:
           return "/admin/hpc/hpcservice/%s/" % services[0].id
       else:
           return "/admin/hpc/hpcservice/"

class CDNPrefixInline(XOSTabularInline):
    model = CDNPrefix
    extra = 0
    suit_classes = 'suit-tab suit-tab-prefixes'
    fields = ('backend_status_icon', 'cdn_prefix_id', 'prefix', 'defaultOriginServer', 'enabled')
    readonly_fields = ('backend_status_icon', 'cdn_prefix_id',)

class OriginServerInline(XOSTabularInline):
    model = OriginServer
    extra = 0
    suit_classes = 'suit-tab suit-tab-origins'
    fields = ('backend_status_icon', 'origin_server_id', 'url')
    readonly_fields = ('backend_status_icon', 'origin_server_id')

class ContentProviderInline(XOSTabularInline):
    model = ContentProvider
    extra = 0
    suit_classes = 'suit-tab suit-tab-cps'
    fields = ('backend_status_icon', 'content_provider_id', 'name', 'enabled')
    readonly_fields = ('backend_status_icon', 'content_provider_id',)

class OriginServerAdmin(HPCAdmin):
    list_display = ('backend_status_icon', 'url','protocol','redirects','contentProvider','authenticated','enabled' )
    list_display_links = ('backend_status_icon', 'url', )

    fields = ('backend_status_text', 'url','protocol','redirects','contentProvider','authenticated','enabled','origin_server_id','description' )
    readonly_fields = ('backend_status_text', 'origin_server_id',)
    user_readonly_fields = ('url','protocol','redirects','contentProvider','authenticated','enabled','origin_server_id','description')

class ContentProviderForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        help_text="Select which users can manage this ContentProvider",
        widget=FilteredSelectMultiple(
            verbose_name=('Users'), is_stacked=False
        )
    )

    class Meta:
        model = ContentProvider
        widgets = {
            'serviceProvider' : LinkedSelect
        }

    def __init__(self, *args, **kwargs):
      request = kwargs.pop('request', None)
      super(ContentProviderForm, self).__init__(*args, **kwargs)

      if self.instance and self.instance.pk:
        self.fields['users'].initial = self.instance.users.all()

class ContentProviderAdmin(HPCAdmin):
    form = ContentProviderForm
    list_display = ('backend_status_icon', 'name','description','enabled' )
    list_display_links = ('backend_status_icon', 'name', )
    readonly_fields = ('backend_status_text', )
    admin_readonly_fields = ('backend_status_text', )
    cp_readonly_fields = ('backend_status_text', 'name', 'enabled', 'serviceProvider', 'users')
    fieldsets = [ (None, {'fields': ['backend_status_text', 'name','enabled','description','serviceProvider','users'], 'classes':['suit-tab suit-tab-general']})]

    inlines = [CDNPrefixInline, OriginServerInline]

    user_readonly_fields = ('name','description','enabled','serviceProvider','users')

    suit_form_tabs = (('general','Details'),('prefixes','CDN Prefixes'), ('origins','Origin Servers'))

    def change_view(self,request, *args, **kwargs):
        if request.user.is_admin:
            self.readonly_fields = self.admin_readonly_fields
        else:
            self.readonly_fields = self.cp_readonly_fields

        return super(ContentProviderAdmin, self).change_view(request, *args, **kwargs)

class ServiceProviderAdmin(HPCAdmin):
    list_display = ('backend_status_icon', 'name', 'description', 'enabled')
    list_display_links = ('backend_status_icon', 'name', )
    fieldsets = [
        (None, {'fields': ['backend_status_text', 'name','description','enabled', 'hpcService'], 'classes':['suit-tab suit-tab-general']})]
#, ('Content Providers', {'fields':['contentProviders'],'classes':['suit-tab suit-tab-cps']})]

    readonly_fields = ('backend_status_text', )
    user_readonly_fields = ('name', 'description', 'enabled')

    suit_form_tabs = (('general','Details'),('cps','Content Providers'))
    inlines = [ContentProviderInline]

class CDNPrefixForm(forms.ModelForm):
    class Meta:
        widgets = {
            'contentProvider' : LinkedSelect
        }

class CDNPrefixAdmin(HPCAdmin):
    form = CDNPrefixForm
    list_display = ['backend_status_icon', 'prefix','contentProvider']
    list_display_links = ('backend_status_icon', 'prefix', )
    fields = ['backend_status_text', 'prefix', 'contentProvider', 'cdn_prefix_id', 'description', 'defaultOriginServer', 'enabled']
    readonly_fields = ('backend_status_text', )
    user_readonly_fields = ['prefix','contentProvider', "cdn_prefix_id", "description", "defaultOriginServer", "enabled"]

class SiteMapAdmin(HPCAdmin):
    model = SiteMap
    verbose_name = "Site Map"
    verbose_name_plural = "Site Map"
    list_display = ("backend_status_icon", "name", "contentProvider", "serviceProvider")
    list_display_links = ('backend_status_icon', 'name', )
    fields = ['backend_status_text', 'name', 'hpcService', 'cdnPrefix', 'contentProvider', 'serviceProvider', 'map', 'map_id']
    user_readonly_fields = ('backend_status_text', "name", "hpcService", "cdnPrefix", "contentProvider", "serviceProvider", "description", "map")
    readonly_fields = ('backend_status_text', )

class AccessMapAdmin(HPCAdmin):
    model = AccessMap
    verbose_name = "Access Map"
    verbose_name_plural = "Access Map"
    list_display = ("backend_status_icon", "name", "contentProvider")
    list_display_links = ('backend_status_icon', 'name', )
    user_readonly_fields = ('backend_status_text', "name", "contentProvider", "description", "map")
    readonly_fields = ('backend_status_text', )

class HpcHealthCheckAdmin(HPCAdmin):
    model = HpcHealthCheck
    verbose_name = "Health Check"
    verbose_name = "Health Checks"
    list_display = ["backend_status_icon", "resource_name", "kind"]
    list_display_links = ["backend_status_icon", "resource_name"]
    fields = ["backend_status_text", "hpcService", "resource_name", "kind", "result_contains", "result_min_size", "result_max_size"]
    readonly_fields = ["backend_status_text",]

admin.site.register(ServiceProvider, ServiceProviderAdmin)
admin.site.register(ContentProvider, ContentProviderAdmin)
admin.site.register(CDNPrefix, CDNPrefixAdmin)
admin.site.register(OriginServer,OriginServerAdmin)
admin.site.register(HpcService, HpcServiceAdmin)
admin.site.register(SiteMap, SiteMapAdmin)
admin.site.register(AccessMap, AccessMapAdmin)
admin.site.register(HpcHealthCheck, HpcHealthCheckAdmin)

