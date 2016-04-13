from django.db import models
from core.models import Service, PlCoreBase, Slice, Instance, Tenant, TenantWithContainer, Node, Image, User, Flavor, Subscriber, NetworkParameter, NetworkParameterType, Port, AddressPool
from core.models.plcorebase import StrippedCharField
import os
from django.db import models, transaction
from django.forms.models import model_to_dict
from django.db.models import Q
from operator import itemgetter, attrgetter, methodcaller
from core.models import Tag
from core.models.service import LeastLoadedNodeScheduler
import traceback
from xos.exceptions import *
from xos.config import Config

class ConfigurationError(Exception):
    pass

VROUTER_KIND = "vROUTER"

CORD_USE_VTN = getattr(Config(), "networking_use_vtn", False)

class VRouterService(Service):
    KIND = VROUTER_KIND

    class Meta:
        app_label = "cord"
        verbose_name = "vRouter Service"
        proxy = True

    def ip_to_mac(self, ip):
        (a, b, c, d) = ip.split('.')
        return "02:42:%02x:%02x:%02x:%02x" % (int(a), int(b), int(c), int(d))

    def get_gateways(self):
        gateways=[]

        aps = self.addresspools.all()
        for ap in aps:
            gateways.append( {"gateway_ip": ap.gateway_ip, "gateway_mac": ap.gateway_mac} )

        return gateways

    def get_address_pool(self, name):
        ap = AddressPool.objects.filter(name=name, service=self)
        if not ap:
            raise Exception("vRouter unable to find addresspool %s" % name)
        return ap[0]

    def get_tenant(self, **kwargs):
        address_pool_name = kwargs.pop("address_pool_name")

        ap = self.get_address_pool(address_pool_name)

        ip = ap.get_address()
        if not ip:
            raise Exception("AddressPool '%s' has run out of addresses." % ap.name)

        t = VRouterTenant(**kwargs)
        t.public_ip = ip
        t.public_mac = self.ip_to_mac(ip)
        t.address_pool_name = ap.name
        t.save()

        return t

#VRouterService.setup_simple_attributes()

class VRouterTenant(Tenant):
    class Meta:
        proxy = True

    KIND = VROUTER_KIND

    simple_attributes = ( ("public_ip", None),
                          ("public_mac", None),
                          ("address_pool_name", None),
                          )

    @property
    def gateway_ip(self):
        return self.address_pool.gateway_ip

    @property
    def gateway_mac(self):
        return self.address_pool.gateway_mac

