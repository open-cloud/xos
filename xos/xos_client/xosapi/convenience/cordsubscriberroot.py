
# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import json
from xosapi.orm import ORMWrapper, register_convenience_wrapper

class ORMWrapperCordSubscriberRoot(ORMWrapper):
    @property
    def volt(self):
        links = self.subscribed_links.all()
        for link in links:
            # TODO: hardcoded service dependency
            # cast from ServiceInstance to VOLTServiceInstance
            volts = self.stub.VOLTServiceInstance.objects.filter(id = link.provider_service_instance.id)
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
