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
from core.admin import SingletonAdmin,SliceInline,ServiceAttrAsTabInline, SliceROInline,ServiceAttrAsTabROInline, ReadOnlyAwareAdmin, PlStackTabularInline, ReadOnlyTabularInline

class HpcServiceAdmin(SingletonAdmin):
    model = HpcService
    verbose_name = "HPC Service"
    verbose_name_plural = "HPC Service"
    list_display = ("name","enabled")
    fieldsets = [(None, {'fields': ['name','enabled','versionNumber', 'description'], 'classes':['suit-tab suit-tab-general']})]
    inlines = [SliceInline,ServiceAttrAsTabInline]

    user_readonly_fields = ["name", "enabled", "versionNumber", "description"]
    user_readonly_inlines = [SliceROInline, ServiceAttrAsTabROInline]

    suit_form_tabs =(('general', 'HPC Service Details'),
        ('slices','Slices'),
        ('serviceattrs','Additional Attributes'),
    )

class CDNPrefixInline(PlStackTabularInline):
    model = CDNPrefix
    extra = 0
    suit_classes = 'suit-tab suit-tab-prefixes'
    fields = ('cdn_prefix_id', 'prefix', 'defaultOriginServer', 'enabled')
    readonly_fields = ('cdn_prefix_id',)

class CDNPrefixROInline(ReadOnlyTabularInline):
    model = CDNPrefix
    extra = 0
    suit_classes = 'suit-tab suit-tab-prefixes'
    fields = ('cdn_prefix_id', 'prefix', 'defaultOriginServer', 'enabled')
    readonly_fields = ('cdn_prefix_id',)

class ContentProviderInline(PlStackTabularInline):
    model = ContentProvider
    extra = 0
    suit_classes = 'suit-tab suit-tab-cps'
    fields = ('content_provider_id', 'name', 'enabled')
    readonly_fields = ('content_provider_id',)

class ContentProviderROInline(ReadOnlyTabularInline):
    model = ContentProvider
    extra = 0
    suit_classes = 'suit-tab suit-tab-cps'

class OriginServerAdmin(ReadOnlyAwareAdmin):
    list_display = ('url','protocol','redirects','contentProvider','authenticated','enabled' )

    fields = ('url','protocol','redirects','contentProvider','authenticated','enabled','origin_server_id','description' )
    readonly_fields = ('origin_server_id',)
    user_readonly_fields = ('url','protocol','redirects','contentProvider','authenticated','enabled','origin_server_id','description')

class ContentProviderForm(forms.ModelForm):
    class Meta:
        widgets = {
            'serviceProvider' : LinkedSelect
        }

class ContentProviderAdmin(ReadOnlyAwareAdmin):
    form = ContentProviderForm
    list_display = ('name','description','enabled' )
    fieldsets = [ (None, {'fields': ['name','enabled','description','serviceProvider','users'], 'classes':['suit-tab suit-tab-general']})]

    inlines = [CDNPrefixInline]

    user_readonly_fields = ('name','description','enabled','serviceProvider','users')
    user_readonly_inlines = [CDNPrefixROInline]

    suit_form_tabs = (('general','Details'),('prefixes','CDN Prefixes'))

class ServiceProviderAdmin(ReadOnlyAwareAdmin):
    list_display = ('name', 'description', 'enabled')
    fieldsets = [
        (None, {'fields': ['name','description','enabled'], 'classes':['suit-tab suit-tab-general']})]
#, ('Content Providers', {'fields':['contentProviders'],'classes':['suit-tab suit-tab-cps']})]

    user_readonly_fields = ('name', 'description', 'enabled')
    user_readonly_inlines = [ContentProviderROInline]

    suit_form_tabs = (('general','Details'),('cps','Content Providers'))
    inlines = [ContentProviderInline]

class CDNPrefixForm(forms.ModelForm):
    class Meta:
        widgets = {
            'contentProvider' : LinkedSelect
        }

class CDNPrefixAdmin(ReadOnlyAwareAdmin):
    form = CDNPrefixForm
    list_display = ['prefix','contentProvider']
    fields = ['prefix', 'contentProvider', 'cdn_prefix_id', 'description', 'defaultOriginServer', 'enabled']
    user_readonly_fields = ['prefix','contentProvider', "cdn_prefix_id", "description", "defaultOriginServer", "enabled"]

class SiteMapAdmin(ReadOnlyAwareAdmin):
    model = SiteMap
    verbose_name = "Site Map"
    verbose_name_plural = "Site Map"
    list_display = ("name", "contentProvider", "serviceProvider")
    user_readonly_fields = ("name", "contentProvider", "serviceProvider", "description", "map")

class AccessMapAdmin(ReadOnlyAwareAdmin):
    model = AccessMap
    verbose_name = "Access Map"
    verbose_name_plural = "Access Map"
    list_display = ("name", "contentProvider")
    user_readonly_fields = ("name", "contentProvider", "description", "map")

admin.site.register(ServiceProvider, ServiceProviderAdmin)
admin.site.register(ContentProvider, ContentProviderAdmin)
admin.site.register(CDNPrefix, CDNPrefixAdmin)
admin.site.register(OriginServer,OriginServerAdmin)
admin.site.register(HpcService, HpcServiceAdmin)
admin.site.register(SiteMap, SiteMapAdmin)
admin.site.register(AccessMap, AccessMapAdmin)

