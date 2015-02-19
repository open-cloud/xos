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
from core.admin import SingletonAdmin,SliceInline,ServiceAttrAsTabInline, ReadOnlyAwareAdmin, XOSTabularInline

class HpcServiceAdmin(SingletonAdmin):
    model = HpcService
    verbose_name = "HPC Service"
    verbose_name_plural = "HPC Service"
    list_display = ("backend_status_icon", "name","enabled")
    list_display_links = ('backend_status_icon', 'name', )
    fieldsets = [(None, {'fields': ['backend_status_text', 'name','enabled','versionNumber', 'description'], 'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', )
    inlines = [SliceInline,ServiceAttrAsTabInline]

    user_readonly_fields = ["name", "enabled", "versionNumber", "description"]

    suit_form_tabs =(('general', 'HPC Service Details'),
        ('slices','Slices'),
        ('serviceattrs','Additional Attributes'),
    )

class CDNPrefixInline(XOSTabularInline):
    model = CDNPrefix
    extra = 0
    suit_classes = 'suit-tab suit-tab-prefixes'
    fields = ('backend_status_icon', 'cdn_prefix_id', 'prefix', 'defaultOriginServer', 'enabled')
    readonly_fields = ('backend_status_icon', 'cdn_prefix_id',)

class ContentProviderInline(XOSTabularInline):
    model = ContentProvider
    extra = 0
    suit_classes = 'suit-tab suit-tab-cps'
    fields = ('backend_status_icon', 'content_provider_id', 'name', 'enabled')
    readonly_fields = ('backend_status_icon', 'content_provider_id',)

class OriginServerAdmin(ReadOnlyAwareAdmin):
    list_display = ('backend_status_icon', 'url','protocol','redirects','contentProvider','authenticated','enabled' )
    list_display_links = ('backend_status_icon', 'url', )

    fields = ('backend_status_text', 'url','protocol','redirects','contentProvider','authenticated','enabled','origin_server_id','description' )
    readonly_fields = ('backend_status_text', 'origin_server_id',)
    user_readonly_fields = ('url','protocol','redirects','contentProvider','authenticated','enabled','origin_server_id','description')

class ContentProviderForm(forms.ModelForm):
    class Meta:
        widgets = {
            'serviceProvider' : LinkedSelect
        }

class ContentProviderAdmin(ReadOnlyAwareAdmin):
    form = ContentProviderForm
    list_display = ('backend_status_icon', 'name','description','enabled' )
    list_display_links = ('backend_status_icon', 'name', )
    fieldsets = [ (None, {'fields': ['backend_status_text', 'name','enabled','description','serviceProvider','users'], 'classes':['suit-tab suit-tab-general']})]
    readonly_fields = ('backend_status_text', )

    inlines = [CDNPrefixInline]

    user_readonly_fields = ('name','description','enabled','serviceProvider','users')

    suit_form_tabs = (('general','Details'),('prefixes','CDN Prefixes'))

class ServiceProviderAdmin(ReadOnlyAwareAdmin):
    list_display = ('backend_status_icon', 'name', 'description', 'enabled')
    list_display_links = ('backend_status_icon', 'name', )
    fieldsets = [
        (None, {'fields': ['backend_status_text', 'name','description','enabled'], 'classes':['suit-tab suit-tab-general']})]
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

class CDNPrefixAdmin(ReadOnlyAwareAdmin):
    form = CDNPrefixForm
    list_display = ['backend_status_icon', 'prefix','contentProvider']
    list_display_links = ('backend_status_icon', 'prefix', )
    fields = ['backend_status_text', 'prefix', 'contentProvider', 'cdn_prefix_id', 'description', 'defaultOriginServer', 'enabled']
    readonly_fields = ('backend_status_text', )
    user_readonly_fields = ['prefix','contentProvider', "cdn_prefix_id", "description", "defaultOriginServer", "enabled"]

class SiteMapAdmin(ReadOnlyAwareAdmin):
    model = SiteMap
    verbose_name = "Site Map"
    verbose_name_plural = "Site Map"
    list_display = ("backend_status_icon", "name", "contentProvider", "serviceProvider")
    list_display_links = ('backend_status_icon', 'name', )
    user_readonly_fields = ('backend_status_text', "name", "contentProvider", "serviceProvider", "description", "map")
    readonly_fields = ('backend_status_text', )

class AccessMapAdmin(ReadOnlyAwareAdmin):
    model = AccessMap
    verbose_name = "Access Map"
    verbose_name_plural = "Access Map"
    list_display = ("backend_status_icon", "name", "contentProvider")
    list_display_links = ('backend_status_icon', 'name', )
    user_readonly_fields = ('backend_status_text', "name", "contentProvider", "description", "map")
    readonly_fields = ('backend_status_text', )

admin.site.register(ServiceProvider, ServiceProviderAdmin)
admin.site.register(ContentProvider, ContentProviderAdmin)
admin.site.register(CDNPrefix, CDNPrefixAdmin)
admin.site.register(OriginServer,OriginServerAdmin)
admin.site.register(HpcService, HpcServiceAdmin)
admin.site.register(SiteMap, SiteMapAdmin)
admin.site.register(AccessMap, AccessMapAdmin)

