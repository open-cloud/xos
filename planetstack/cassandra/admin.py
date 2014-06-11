from django.contrib import admin

from cassandra.models import *
from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone
from django.contrib.contenttypes import generic
from suit.widgets import LinkedSelect
from core.admin import SingletonAdmin,SliceInline,ServiceAttrAsTabInline, SliceROInline,ServiceAttrAsTabROInline, ReadOnlyAwareAdmin

class CassandraServiceAdmin(SingletonAdmin):
    model = CassandraService
    verbose_name = "Cassandra Service"
    verbose_name_plural = "Cassandra Service"
    list_display = ("name","enabled")
    fieldsets = [(None, {'fields': ['name','enabled','versionNumber', 'description','clusterSize','replicationFactor'], 'classes':['suit-tab suit-tab-general']})]
    inlines = [SliceInline,ServiceAttrAsTabInline]

    user_readonly_inlines = [SliceROInline, ServiceAttrAsTabROInline]
    user_readonly_fields = ["name", "enabled", "versionNumber", "description", "clusterSize", "replicationFactor"]

    suit_form_tabs =(('general', 'Cassandra Service Details'),
        ('slices','Slices'),
        ('serviceattrs','Additional Attributes'),
    )

admin.site.register(CassandraService, CassandraServiceAdmin)

