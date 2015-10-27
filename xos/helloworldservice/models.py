from django.db import models
from core.models import Service, PlCoreBase, Slice, Instance, Tenant, TenantWithContainer, Node, Image, User, Flavor, Subscriber
from core.models.plcorebase import StrippedCharField
import os
from django.db import models, transaction
from django.forms.models import model_to_dict
from django.db.models import Q
from operator import itemgetter, attrgetter, methodcaller
import traceback
from xos.exceptions import *
from core.models import SlicePrivilege, SitePrivilege
from sets import Set
from core.models.plcorebase import StrippedCharField


HELLO_WORLD_KIND = "helloworldservice"

class HelloWorldService(Service):
    KIND = HELLO_WORLD_KIND

    class Meta:
	proxy = True
        app_label = "helloworldservice"
        verbose_name = "Hello World Service"

class HelloWorldTenant(TenantWithContainer):
    class Meta:
        proxy = True

    KIND = HELLO_WORLD_KIND
    default_attributes = {'display_message': 'Hello World!'}
    def __init__(self, *args, **kwargs):
        hello_world_service_services = HelloWorldService.get_service_objects().all()
        if hello_world_service_services:
            self._meta.get_field("provider_service").default = hello_world_service_services[0].id
        super(HelloWorldTenant, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.creator:
            if not getattr(self, "caller", None):
                # caller must be set when creating a vCPE since it creates a slice
                raise XOSProgrammingError("HelloWorldTennant's self.caller was not set")
            self.creator = self.caller
            if not self.creator:
                raise XOSProgrammingError("HelloWorldTennant's self.creator was not set")

        super(HelloWorldTenant, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.cleanup_container()
        super(HelloWorldTenant, self).delete(*args, **kwargs)

    @property
    def display_message(self):
	return self.get_attribute("display_message", self.default_attributes['display_message'])

    @display_message.setter
    def display_message(self, value):
        self.set_attribute("display_message", value)
