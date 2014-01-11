from django.contrib import admin

from syndicate.models import *
from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone
from django.contrib.contenttypes import generic
from suit.widgets import LinkedSelect
from core.admin import ReadOnlyTabularInline,ReadOnlyAwareAdmin,SingletonAdmin,SliceInline,ServiceAttrAsTabInline,PlanetStackBaseAdmin, PlStackTabularInline,SliceROInline,ServiceAttrAsTabROInline
from suit.widgets import LinkedSelect
from bitfield import BitField
from bitfield.forms import BitFieldCheckboxSelectMultiple

class SyndicateServiceAdmin(SingletonAdmin,ReadOnlyAwareAdmin):
    model = SyndicateService
    verbose_name = "Syndicate Service"
    verbose_name_plural = "Syndicate Service"
    list_display = ("name","enabled")
    fieldsets = [(None, {'fields': ['name','enabled','versionNumber', 'description',], 'classes':['suit-tab suit-tab-general']})]
    inlines = [SliceInline,ServiceAttrAsTabInline]

    user_readonly_fields = ['name','enabled','versionNumber','description']
    user_readonly_inlines = [SliceROInline, ServiceAttrAsTabROInline]

    suit_form_tabs =(('general', 'Syndicate Service Details'),
        ('slices','Slices'),
        ('serviceattrs','Additional Attributes'),
    )

class VolumeAccessRightForUserROInline(ReadOnlyTabularInline):
    model = VolumeAccessRight
    extra = 0
    suit_classes = 'suit-tab suit-tab-volumeAccessRights'
    fields = ['volume','gateway_caps']

class VolumeAccessRightROInline(ReadOnlyTabularInline):
    model = VolumeAccessRight
    extra = 0
    suit_classes = 'suit-tab suit-tab-volumeAccessRights'
    fields = ['owner_id','gateway_caps']

class VolumeAccessRightInline(PlStackTabularInline):
    model = VolumeAccessRight
    extra = 0
    suit_classes = 'suit-tab suit-tab-volumeAccessRights'

class VolumeAccessRightAdmin(ReadOnlyAwareAdmin):
    model = VolumeAccessRight

    formfield_overrides = { BitField: {'widget': BitFieldCheckboxSelectMultiple},}
    list_display = ['owner_id', 'volume']
    user_readonly_fields = ['owner_id','volume','gateway_caps']
    user_readonly_inlines = []

class VolumeAccessRequestForUserROInline(ReadOnlyTabularInline):
    model = VolumeAccessRequest
    extra = 0
    suit_classes = 'suit-tab suit-tab-volumeAccessRequests'
    fields = ['volume', 'message']

class VolumeAccessRequestROInline(ReadOnlyTabularInline):
    model = VolumeAccessRequest
    extra = 0
    suit_classes = 'suit-tab suit-tab-volumeAccessRequests'
    fields = ['owner_id', 'message']

class VolumeAccessRequestInline(PlStackTabularInline):
    model = VolumeAccessRequest
    extra = 0
    suit_classes = 'suit-tab suit-tab-volumeAccessRequests'
    fields = ['owner_id', 'message']

class VolumeAccessRequestAdmin(ReadOnlyAwareAdmin):
    model = VolumeAccessRequest

    formfield_overrides = { BitField: {'widget': BitFieldCheckboxSelectMultiple},}
    list_display = ['owner_id', 'volume', 'message']
    user_readonly_fields = ['volume','owner_id','message','message', 'gateway_caps']
    user_readonly_inlines = []

class VolumeInline(PlStackTabularInline):
    model = Volume
    extra = 0
    suit_classes = 'suit-tab suit-tab-volumes'
    fields = ['name', 'owner_id']

class VolumeROInline(ReadOnlyTabularInline):
    model = Volume
    extra = 0
    suit_classes = 'suit-tab suit-tab-volumes'
    fields = ['name', 'owner_id']

class VolumeAdmin(ReadOnlyAwareAdmin):
    model = Volume
    read_only_fields = ['blockSize']
    list_display = ['name', 'owner_id']

    formfield_overrides = { BitField: {'widget': BitFieldCheckboxSelectMultiple},}

    detailsFieldList = ['name', 'owner_id', 'description','file_quota','blocksize', 'private','archive', 'default_gateway_caps' ]
    keyList = ['metadata_public_key','metadata_private_key','api_public_key']

    fieldsets = [
        (None, {'fields': detailsFieldList, 'classes':['suit-tab suit-tab-general']}),
        (None, {'fields': keyList, 'classes':['suit-tab suit-tab-volumeKeys']}),
    ]

    inlines = [VolumeAccessRightInline, VolumeAccessRequestInline]

    user_readonly_fields = ['name','owner_id','description','blocksize','private','metadata_public_key','metadata_private_key','api_public_key','file_quota','default_gateway_caps']
    user_readonly_inlines = [VolumeAccessRightROInline, VolumeAccessRequestROInline]

    suit_form_tabs =(('general', 'Volume Details'),
                     ('volumeKeys', 'Access Keys'),
                     ('volumeAccessRequests', 'Volume Access Requests'),
                     ('volumeAccessRights', 'Volume Access Rights'),
    )
    
    

class SyndicateUserAdmin(ReadOnlyAwareAdmin):
    model = SyndicateUser
    verbose_name = "Users"
    verbose_name = "Users"
    list_display = ['user','is_admin', 'max_volumes']
    inlines = [VolumeInline,VolumeAccessRequestInline,VolumeAccessRightInline]
    user_readonly_fields = ['user','is_admin','max_volumes','max_UGs','max_RGs','max_AGs']
    user_readonly_inlines = [VolumeROInline,VolumeAccessRequestForUserROInline,VolumeAccessRightForUserROInline]

    fieldsets = [
        (None, {'fields': ['user','is_admin','max_volumes','max_UGs','max_RGs','max_AGs'], 'classes':['suit-tab suit-tab-general']}),
    ]

    suit_form_tabs =(('general', 'Volume Details'),
                     ('volumes', 'Volumes'),
                     ('volumeAccessRequests', 'Volume Access Requests'),
                     ('volumeAccessRights', 'Volume Access Rights'),
    )

admin.site.register(SyndicateService, SyndicateServiceAdmin)
admin.site.register(VolumeAccessRight, VolumeAccessRightAdmin)
admin.site.register(VolumeAccessRequest, VolumeAccessRequestAdmin)
admin.site.register(Volume, VolumeAdmin)
admin.site.register(SyndicateUser, SyndicateUserAdmin)

