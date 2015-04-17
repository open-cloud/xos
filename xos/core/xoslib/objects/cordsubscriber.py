from core.models import Slice, SlicePrivilege, SliceRole, Sliver, Site, Node, User
from cord.models import VOLTTenant
from plus import PlusObjectMixin
from operator import itemgetter, attrgetter
from rest_framework.exceptions import APIException

"""
import os
import sys
sys.path.append("/opt/xos")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xos.settings")
import django
from core.models import *
from hpc.models import *
from cord.models import *
django.setup()
from core.xoslib.objects.cordsubscriber import CordSubscriber
c=CordSubscriber.get_tenant_objects().select_related().all()[0]
"""

class CordSubscriber(VOLTTenant, PlusObjectMixin):
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(VOLTTenant, self).__init__(*args, **kwargs)

    @property
    def vcpe_id(self):
        if self.vcpe:
            return self.vcpe.id
        else:
            return None

    @vcpe_id.setter
    def vcpe_id(self, value):
        pass

    passthroughs = ( ("firewall_enable", "vcpe.firewall_enable"),
                     ("firewall_rules", "vcpe.firewall_rules"),
                     ("url_filter_enable", "vcpe.url_filter_enable"),
                     ("url_filter_rules", "vcpe.url_filter_rules"),
                     ("cdn_enable", "vcpe.cdn_enable"),
                     ("image", "vcpe.image.id"),
                     ("image_name", "vcpe.image.name"),
                     ("sliver", "vcpe.sliver.id"),
                     ("sliver_name", "vcpe.sliver.name") )

    def __getattr__(self, key):
        for (member_name, passthrough_name) in self.passthroughs:
            if key==member_name:
                parts = passthrough_name.split(".")
                obj = self
                for part in parts[:-1]:
                    obj = getattr(obj, part)
                    if not obj:
                        return None
                return getattr(obj, parts[-1])

        raise AttributeError("getattr: %r object has no attribute %r" %
                         (self.__class__, key))

    def __setattr__(self, key, value):
        for (member_name, passthrough_name) in self.passthroughs:
            if key==member_name:
                parts = passthrough_name.split(".")
                obj = self
                for part in parts[:-1]:
                     obj = getattr(obj, part)
                     if not obj:
                         return
                setattr(obj, parts[-1], value)

        super(CordSubscriber, self).__setattr__(key, value)








