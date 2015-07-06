from core.models import Slice, SlicePrivilege, SliceRole, Sliver, Site, Node, User
from cord.models import VOLTTenant, CordSubscriberRoot
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
        super(CordSubscriber, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return u"cordSubscriber-%s" % str(self.id)

    passthroughs = ( ("firewall_enable", "vcpe.firewall_enable"),
                     ("firewall_rules", "vcpe.firewall_rules"),
                     ("url_filter_enable", "vcpe.url_filter_enable"),
                     ("url_filter_rules", "vcpe.url_filter_rules"),
                     ("url_filter_level", "vcpe.url_filter_level"),
                     ("ssh_command", "vcpe.ssh_command"),
                     ("bbs_account", "vcpe.bbs_account"),
                     ("users", "vcpe.users"),
                     ("services", "vcpe.services"),
                     ("cdn_enable", "vcpe.cdn_enable"),
                     ("image", "vcpe.image.id"),
                     ("image_name", "vcpe.image.name"),
                     ("sliver", "vcpe.sliver.id"),
                     ("sliver_name", "vcpe.sliver.name"),
                     ("routeable_subnet", "vcpe.vbng.routeable_subnet"),
                     ("vcpe_id", "vcpe.id"),
                     ("vbng_id", "vcpe.vbng.id"),
                     ("nat_ip", "vcpe.nat_ip"),
                     ("lan_ip", "vcpe.lan_ip"),
                     ("private_ip", "vcpe.private_ip"),
                     ("wan_ip", "vcpe.wan_ip"),
                     ("wan_mac", "vcpe.wan_mac"),
                     ("vcpe_synced", "vcpe.is_synced"),
                     )

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

    def save(self, *args, **kwargs):
        super(CordSubscriber, self).save(*args, **kwargs)

        # in case the vcpe or vbng fields were altered
        #   TODO: dirty detection?
        if (self.vcpe):
            print "save vcpe"
            self.vcpe.save()
            if (self.vcpe.vbng):
                print "save vbng", self.vcpe.vbng
                print "attr", self.vcpe.vbng.service_specific_attribute
                self.vcpe.vbng.save()

class CordSubscriberNew(CordSubscriberRoot):
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(CordSubscriber, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return u"cordSubscriber-%s" % str(self.id)

    passthroughs = ( # the following are now fields of CordSubscriberRoot
                     # ("firewall_enable", "vcpe.firewall_enable"),
                     # ("firewall_rules", "vcpe.firewall_rules"),
                     # ("url_filter_enable", "vcpe.url_filter_enable"),
                     # ("url_filter_rules", "vcpe.url_filter_rules"),
                     # ("url_filter_level", "vcpe.url_filter_level"),
                     # ("bbs_account", "vcpe.bbs_account"),
                     # ("users", "vcpe.users"),
                     # ("services", "vcpe.services"),
                     # ("cdn_enable", "vcpe.cdn_enable"),

                     ("ssh_command", "volt.vcpe.ssh_command"),
                     ("image", "volt.vcpe.image.id"),
                     ("image_name", "volt.vcpe.image.name"),
                     ("sliver", "volt.vcpe.sliver.id"),
                     ("sliver_name", "volt.vcpe.sliver.name"),
                     ("routeable_subnet", "volt.vcpe.vbng.routeable_subnet"),
                     ("vcpe_id", "volt.vcpe.id"),
                     ("vbng_id", "volt.vcpe.vbng.id"),
                     ("nat_ip", "volt.vcpe.nat_ip"),
                     ("lan_ip", "volt.vcpe.lan_ip"),
                     ("private_ip", "volt.vcpe.private_ip"),
                     ("wan_ip", "volt.vcpe.wan_ip"),
                     ("wan_mac", "volt.vcpe.wan_mac"),
                     ("vcpe_synced", "volt.vcpe.is_synced"),
                     )

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

    def save(self, *args, **kwargs):
        super(CordSubscriber, self).save(*args, **kwargs)

        # in case the vcpe or vbng fields were altered
        #   TODO: dirty detection?
        if (self.volt):
            print "save volt"
            self.volt.save()
            if (self.vcpe):
                print "save vcpe"
                self.vcpe.save()
                if (self.vcpe.vbng):
                    print "save vbng", self.vcpe.vbng
                    print "attr", self.vcpe.vbng.service_specific_attribute
                    self.vcpe.vbng.save()








