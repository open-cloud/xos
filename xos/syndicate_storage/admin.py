from django.contrib import admin

from syndicate_storage.models import *
from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone
from django.contrib.contenttypes import generic
from suit.widgets import LinkedSelect
from core.admin import ReadOnlyAwareAdmin,ServiceAppAdmin,SliceInline,ServiceAttrAsTabInline,XOSBaseAdmin, XOSTabularInline
from suit.widgets import LinkedSelect
from django.core.exceptions import ValidationError, ObjectDoesNotExist

class SyndicateAdmin(ReadOnlyAwareAdmin):
   # Change the application breadcrumb to point to an RR Service if one is
   # defined

   change_form_template = "admin/change_form_bc.html"
   change_list_template = "admin/change_list_bc.html"
   custom_app_breadcrumb_name = "Syndicate_Storage"
   @property
   def custom_app_breadcrumb_url(self):
       services = SyndicateService.objects.all()
       if len(services)==1:
           return "/admin/syndicate_storage/syndicateservice/%s/" % services[0].id
       else:
           return "/admin/syncdicate_storage/syndicateservice/"

class SyndicateServiceAdmin(ServiceAppAdmin):
    model = SyndicateService
    verbose_name = "Syndicate Storage"
    verbose_name_plural = "Syndicate Storage"
    list_display = ("name","enabled")
    fieldsets = [(None, {'fields': ['name','enabled','versionNumber', 'description',], 'classes':['suit-tab suit-tab-general']})]
    inlines = [SliceInline,ServiceAttrAsTabInline]

    user_readonly_fields = ['name','enabled','versionNumber','description']

    suit_form_tabs =(('general', 'Syndicate Storage Details'),
        ('administration', 'Administration'),
        ('slices','Slices'),
        ('serviceattrs','Additional Attributes'),
    )

    suit_form_includes = (('syndicateadmin.html', 'top', 'administration'),)


class VolumeAccessRightInline(XOSTabularInline):
    model = VolumeAccessRight
    extra = 0
    suit_classes = 'suit-tab suit-tab-volumeAccessRights'


class VolumeSliceFormSet( forms.models.BaseInlineFormSet ):
    # verify that our VolumeSlice is valid

    @classmethod
    def verify_unchanged( cls, volume_pk, slice_pk, field_name, new_value ):
        vs = None
        try:
           vs = VolumeSlice.objects.get( volume_id=volume_pk, slice_id=slice_pk )
        except ObjectDoesNotExist, dne:
           return True, None

        old_value = getattr( vs, field_name )
        if old_value != new_value:
            return False, old_value
        else:
            return True, None


    def clean( self ):
        for form in self.forms:
            # check each inline's cleaned data, if it's valid
            cleaned_data = None
            try:
                if form.cleaned_data:
                    cleaned_data = form.cleaned_data
            except AttributeError:
                continue
             
            # verify that the ports haven't changed 
            volume_pk = cleaned_data['volume_id'].pk
            slice_pk = cleaned_data['slice_id'].pk
           
            if not cleaned_data.has_key('UG_portnum'):
                raise ValidationError("Missing UG port number")

            if not cleaned_data.has_key('RG_portnum'):
                raise ValidationError("Missing RG port number")

            rc1, old_peer_port = VolumeSliceFormSet.verify_unchanged( volume_pk, slice_pk, 'UG_portnum', cleaned_data['UG_portnum'] )
            rc2, old_replicate_port = VolumeSliceFormSet.verify_unchanged( volume_pk, slice_pk, 'RG_portnum', cleaned_data['RG_portnum'] )

            err1str = ""
            err2str = ""
            if not rc1:
                err1str = "change %s back to %s" % (cleaned_data['UG_portnum'], old_peer_port)
            if not rc2:
                err2str = " and change %s back to %s" % (cleaned_data['RG_portnum'], old_replicate_port )

            if not rc1 or not rc2:
                raise ValidationError("At this time, port numbers cannot be changed once they are set. Please %s %s" % (err1str, err2str))
            
            

class VolumeSliceInline(XOSTabularInline):
    model = VolumeSlice
    extra = 0
    suit_classes = 'suit-tab suit-tab-volumeSlices'
    fields = ['volume_id', 'slice_id', 'cap_read_data', 'cap_write_data', 'cap_host_data', 'UG_portnum', 'RG_portnum']

    formset = VolumeSliceFormSet
    
    readonly_fields = ['credentials_blob']
 

class VolumeAdmin(SyndicateAdmin):
    model = Volume
   
    def get_readonly_fields(self, request, obj=None ):
       always_readonly = []
       if obj == None:
          # all fields are editable on add
          return always_readonly

       else:
          # can't change owner, slice id, or block size on update
          return ['blocksize', 'owner_id'] + always_readonly


    list_display = ['name', 'owner_id']

    detailsFieldList = ['name', 'owner_id', 'description','blocksize', 'private','archive', 'cap_read_data', 'cap_write_data', 'cap_host_data' ]

    fieldsets = [
        (None, {'fields': detailsFieldList, 'classes':['suit-tab suit-tab-general']}),
    ]

    inlines = [VolumeAccessRightInline, VolumeSliceInline]

    user_readonly_fields = ['name','owner_id','description','blocksize','private', 'archive', 'cap_read_data', 'cap_write_data', 'cap_host_data']
    
    suit_form_tabs =(('general', 'Volume Details'),
                     ('volumeSlices', 'Slices'),
                     ('volumeAccessRights', 'Volume Access Rights'))
    
    def queryset(self, request):
       # only show volumes that are public, or owned by the caller 
       return Volume.select_by_user(request.user)
    
    
# left panel:
admin.site.register(SyndicateService, SyndicateServiceAdmin)
admin.site.register(Volume, VolumeAdmin)
