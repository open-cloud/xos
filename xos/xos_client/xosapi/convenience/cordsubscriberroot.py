import json
from xosapi.orm import ORMWrapper, register_convenience_wrapper

class ORMWrapperCordSubscriberRoot(ORMWrapper):
    @property
    def volt(self):
        volt_tenants = self.stub.VOLTTenant.objects.filter(subscriber_root_id = self.id)
        if volt_tenants:
            return volt_tenants[0]
        return None

    # all of these will go away when CordSubscriberRoot is made into a real object

    sync_attributes = ("firewall_enable",
                       "firewall_rules",
                       "url_filter_enable",
                       "url_filter_rules",
                       "cdn_enable",
                       "uplink_speed",
                       "downlink_speed",
                       "enable_uverse",
                       "status")

    def get_attribute(self, name, default=None):
        if self.service_specific_attribute:
            attributes = json.loads(self.service_specific_attribute)
        else:
            attributes = {}
        return attributes.get(name, default)

    @property
    def firewall_enable(self):
        return self.get_attribute("firewall_enable", False)

    @property
    def firewall_rules(self):
        return self.get_attribute("firewall_rules", "accept all anywhere anywhere")

    @property
    def url_filter_enable(self):
        return self.get_attribute("url_filter_enable", False)

    @property
    def url_filter_rules(self):
        return self.get_attribute("url_filter_rules", "allow all")

    @property
    def url_filter_level(self):
        return self.get_attribute("url_filter_level", "PG")

    @property
    def cdn_enable(self):
        return self.get_attribute("cdn_enable", False)

    @property
    def devices(self):
        return self.get_attribute("devices", [])

    @property
    def is_demo_user(self):
        return self.get_attribute("is_demo_user", False)

    @property
    def uplink_speed(self):
        return self.get_attribute("uplink_speed", 1000000000)

    @property
    def downlink_speed(self):
        return self.get_attribute("downlink_speed", 1000000000)

    @property
    def enable_uverse(self):
        return self.get_attribute("enable_uverse", True)

    @property
    def status(self):
        return self.get_attribute("status", "enabled")

register_convenience_wrapper("CordSubscriberRoot", ORMWrapperCordSubscriberRoot)
