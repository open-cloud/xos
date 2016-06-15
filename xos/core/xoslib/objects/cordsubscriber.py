from core.models import Slice, SlicePrivilege, SliceRole, Instance, Site, Node, User
from services.volt.models import VOLTTenant, CordSubscriberRoot
from plus import PlusObjectMixin
from operator import itemgetter, attrgetter
from rest_framework.exceptions import APIException

class CordSubscriber(CordSubscriberRoot):
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
                     # ("users", "vcpe.users"),
                     # ("services", "vcpe.services"),
                     # ("cdn_enable", "vcpe.cdn_enable"),
                     # uplink_speed, downlink_speed, status, enable_uverse

                     ("c_tag", "volt.c_tag"),
                     ("s_tag", "volt.s_tag"),

                     ("bbs_account", "volt.vcpe.bbs_account"),
                     ("ssh_command", "volt.vcpe.ssh_command"),
                     ("image", "volt.vcpe.image.id"),
                     ("image_name", "volt.vcpe.image.name"),
                     ("instance", "volt.vcpe.instance.id"),
                     ("instance_name", "volt.vcpe.instance.name"),
                     ("routeable_subnet", "volt.vcpe.vbng.routeable_subnet"),
                     ("vcpe_id", "volt.vcpe.id"),
                     ("vbng_id", "volt.vcpe.vbng.id"),
                     ("nat_ip", "volt.vcpe.nat_ip"),
                     ("lan_ip", "volt.vcpe.lan_ip"),
                     ("private_ip", "volt.vcpe.private_ip"),
                     ("wan_ip", "volt.vcpe.wan_ip"),
                     ("wan_mac", "volt.vcpe.wan_mac"),
                     ("vcpe_synced", "volt.vcpe.is_synced"),
                     ("wan_container_ip", "volt.vcpe.wan_container_ip"),
                     )

    def __getattr__(self, key):
        #print "XXX getattr", self, key
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
            if (self.volt.vcpe):
                print "save vcpe"
                self.volt.vcpe.save()
                if (self.volt.vcpe.vbng):
                    print "save vbng", self.volt.vcpe.vbng
                    print "attr", self.volt.vcpe.vbng.service_specific_attribute
                    self.volt.vcpe.vbng.save()








