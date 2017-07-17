import json
from xosapi.orm import ORMWrapper, register_convenience_wrapper

class ORMWrapperCordSubscriberRoot(ORMWrapper):
    @property
    def volt(self):
        links = self.subscribed_links.all()
        for link in links:
            # TODO: hardcoded service dependency
            # cast from ServiceInstance to VOLTTenant
            volts = self.stub.VOLTTenant.objects.filter(id = link.provider_service_instance.id)
            if volts:
                return volts[0]
        return None

    sync_attributes = ("firewall_enable",
                       "firewall_rules",
                       "url_filter_enable",
                       "url_filter_rules",
                       "cdn_enable",
                       "uplink_speed",
                       "downlink_speed",
                       "enable_uverse",
                       "status")

    # figure out what to do about "devices"... is it still needed?

    def get_attribute(self, name, default=None):
        if self.service_specific_attribute:
            attributes = json.loads(self.service_specific_attribute)
        else:
            attributes = {}
        return attributes.get(name, default)

    @property
    def devices(self):
        return self.get_attribute("devices", [])

register_convenience_wrapper("CordSubscriberRoot", ORMWrapperCordSubscriberRoot)
