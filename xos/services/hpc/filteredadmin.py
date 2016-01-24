from django.contrib import admin

from django import forms
from services.hpc.models import HpcService
from core.admin import ServiceAppAdmin,SliceInline,ServiceAttrAsTabInline, ReadOnlyAwareAdmin, XOSTabularInline, SliderWidget, ServicePrivilegeInline
from core.middleware import get_request

from functools import update_wrapper
from django.contrib.admin.views.main import ChangeList
from django.core.urlresolvers import reverse, NoReverseMatch
from django.contrib.admin.utils import quote

import threading
_thread_locals = threading.local()

class FilteredChangeList(ChangeList):
    """ A special ChangeList with a doctored url_for_result function that
        points to the filteredchange view instead of the default change
        view.
    """

    def __init__(self, request, *args, **kwargs):
        self.service = getattr(request, "hpcService", None)
        self.embedded = getattr(request, "embedded", False)
        super(FilteredChangeList, self).__init__(request, *args, **kwargs)

    def url_for_result(self, result):
        if (self.service is None):
             return super(FilteredChangeList, self).url_for_result(result)

        pk = getattr(result, self.pk_attname)
        if self.embedded:
            return reverse('admin:%s_%s_embeddedfilteredchange' % (self.opts.app_label,
                                                           self.opts.model_name),
                           args=(quote(self.service.id), quote(pk),),
                           current_app=self.model_admin.admin_site.name)

        else:
            return reverse('admin:%s_%s_filteredchange' % (self.opts.app_label,
                                                           self.opts.model_name),
                           args=(quote(self.service.id), quote(pk),),
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
                if len(request.resolver_match.args)>1:
                    # this is only useful on change views, not changelist views
                    extra_context["custom_delete_url"] = "/admin/hpc/%s/%s/delete/" % (self.model._meta.model_name, request.resolver_match.args[1])

       extra_context["show_save"] = False
       extra_context["show_save_and_add_another"] = False

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

class FilteredInline(XOSTabularInline):
   def get_change_url(self, id):
       request = get_request()
       embedded = getattr(request, "embedded", False)
       service_id = request.resolver_match.args[0]

       if embedded:
           reverse_path = "admin:%s_embeddedfilteredchange" % (self.selflink_model._meta.db_table)
           args = (service_id, id)
       else:
           reverse_path = "admin:%s_filteredchange" % (self.selflink_model._meta.db_table)
           args = (service_id, id)

       try:
           url = reverse(reverse_path, args=args, current_app=self.selflink_model._meta.app_label)
       except NoReverseMatch:
           return None

       return url

