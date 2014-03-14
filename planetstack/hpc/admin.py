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

#class HPCRRBaseAdmin(admin.ModelAdmin):
    #exclude = ['enacted']

class CDNPrefixInline(admin.TabularInline):
    model = CDNPrefix
    extra = 0
    suit_classes = 'suit-tab suit-tab-prefixes'

class ContentProviderInline(admin.TabularInline):
    model = ContentProvider
    extra = 0
    suit_classes = 'suit-tab suit-tab-cps'

class OriginServerAdmin(admin.ModelAdmin):
    list_display = ('url','protocol','redirects','contentProvider','authenticated','enabled' )

class ContentProviderForm(forms.ModelForm):
    class Meta:
        widgets = {
            'serviceProvider' : LinkedSelect
        }

class ContentProviderAdmin(admin.ModelAdmin):
    form = ContentProviderForm
    list_display = ('name','description','enabled' )
    fieldsets = [ (None, {'fields': ['name','enabled','description','serviceProvider','users'], 'classes':['suit-tab suit-tab-general']})]

    inlines = [CDNPrefixInline]

    suit_form_tabs = (('general','Details'),('prefixes','CDN Prefixes'))

class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'enabled')
    fieldsets = [
        (None, {'fields': ['name','description','enabled'], 'classes':['suit-tab suit-tab-general']})]
#, ('Content Providers', {'fields':['contentProviders'],'classes':['suit-tab suit-tab-cps']})] 

    suit_form_tabs = (('general','Details'),('cps','Content Providers'))
    inlines = [ContentProviderInline]

class CDNPrefixForm(forms.ModelForm):
    class Meta:
        widgets = {
            'contentProvider' : LinkedSelect
        }

class CDNPrefixAdmin(admin.ModelAdmin):
    form = CDNPrefixForm
    list_display = ['prefix','contentProvider']

class SiteMapAdmin(admin.ModelAdmin):
    model = SiteMap
    verbose_name = "Site Map"
    verbose_name_plural = "Site Map"
    list_display = ("name", "contentProvider", "serviceProvider")

class AccessMapAdmin(admin.ModelAdmin):
    model = AccessMap
    verbose_name = "Access Map"
    verbose_name_plural = "Access Map"
    list_display = ("name", "contentProvider")

admin.site.register(ServiceProvider, ServiceProviderAdmin)
admin.site.register(ContentProvider, ContentProviderAdmin)
admin.site.register(CDNPrefix, CDNPrefixAdmin)
admin.site.register(OriginServer,OriginServerAdmin)
admin.site.register(HpcService)
admin.site.register(SiteMap, SiteMapAdmin)
admin.site.register(AccessMap, AccessMapAdmin)

