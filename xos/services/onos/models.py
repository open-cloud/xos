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

ONOS_KIND = "onos"

class ONOSService(Service):
    KIND = ONOS_KIND

    class Meta:
        app_label = "onos"
        verbose_name = "ONOS Service"
        proxy = True

class ONOSApp(Tenant):   # aka 'ONOSTenant'
    class Meta:
        proxy = True

    KIND = ONOS_KIND

    default_attributes = {"name": "",
                          "dependencies": ""}
    def __init__(self, *args, **kwargs):
        onos_services = ONOSService.get_service_objects().all()
        if onos_services:
            self._meta.get_field("provider_service").default = onos_services[0].id
        super(ONOSApp, self).__init__(*args, **kwargs)

    @property
    def creator(self):
        from core.models import User
        if getattr(self, "cached_creator", None):
            return self.cached_creator
        creator_id=self.get_attribute("creator_id")
        if not creator_id:
            return None
        users=User.objects.filter(id=creator_id)
        if not users:
            return None
        user=users[0]
        self.cached_creator = users[0]
        return user

    @creator.setter
    def creator(self, value):
        if value:
            value = value.id
        if (value != self.get_attribute("creator_id", None)):
            self.cached_creator=None
        self.set_attribute("creator_id", value)

    @property
    def name(self):
        return self.get_attribute("name", self.default_attributes["name"])

    @name.setter
    def name(self, value):
        self.set_attribute("name", value)

    @property
    def dependencies(self):
        return self.get_attribute("dependencies", self.default_attributes["dependencies"])

    @dependencies.setter
    def dependencies(self, value):
        self.set_attribute("dependencies", value)

    def save(self, *args, **kwargs):
        if not self.creator:
            if not getattr(self, "caller", None):
                # caller must be set when creating a vCPE since it creates a slice
                raise XOSProgrammingError("ONOSApp's self.caller was not set")
            self.creator = self.caller
            if not self.creator:
                raise XOSProgrammingError("ONOSApp's self.creator was not set")

        super(ONOSApp, self).save(*args, **kwargs)
        model_policy_onos_app(self.pk)

# TODO: Probably don't need this...
def model_policy_onos_app(pk):
    # TODO: this should be made in to a real model_policy
    with transaction.atomic():
        oa = ONOSApp.objects.select_for_update().filter(pk=pk)
        if not oa:
            return
        oa = oa[0]
        #oa.manage_container()


