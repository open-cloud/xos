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
        app_label = "vrouter"
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

        t = VRouterTenant(provider_service=self, **kwargs)
        t.public_ip = ip
        t.public_mac = self.ip_to_mac(ip)
        t.address_pool_id = ap.id
        t.save()

        return t

#VRouterService.setup_simple_attributes()

class VRouterTenant(Tenant):
    class Meta:
        proxy = True

    KIND = VROUTER_KIND

    simple_attributes = ( ("public_ip", None),
                          ("public_mac", None),
                          ("address_pool_id", None),
                          )

    @property
    def gateway_ip(self):
        if not self.address_pool:
            return None
        return self.address_pool.gateway_ip

    @property
    def gateway_mac(self):
        if not self.address_pool:
            return None
        return self.address_pool.gateway_mac

    @property
    def cidr(self):
        if not self.address_pool:
            return None
        return self.address_pool.cidr

    @property
    def netbits(self):
        # return number of bits in the network portion of the cidr
        if self.cidr:
            parts = self.cidr.split("/")
            if len(parts)==2:
                return int(parts[1].strip())
        return None

    @property
    def address_pool(self):
        if getattr(self, "cached_address_pool", None):
            return self.cached_address_pool
        if not self.address_pool_id:
            return None
        aps=AddressPool.objects.filter(id=self.address_pool_id)
        if not aps:
            return None
        ap=aps[0]
        self.cached_address_pool = ap
        return ap

    @address_pool.setter
    def address_pool(self, value):
        if value:
            value = value.id
        if (value != self.get_attribute("address_pool_id", None)):
            self.cached_address_pool=None
        self.set_attribute("address_pool_id", value)

    def cleanup_addresspool(self):
        if self.address_pool_id:
            ap = AddressPool.objects.filter(id=self.address_pool_id)
            if ap:
                ap[0].put_address(self.public_ip)
                self.public_ip = None

    def delete(self, *args, **kwargs):
        self.cleanup_addresspool()
        super(VRouterTenant, self).delete(*args, **kwargs)

VRouterTenant.setup_simple_attributes()

