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


from __future__ import absolute_import

from multistructlog import create_logger
from xosapi.orm import ORMWrapper, register_convenience_wrapper
from xosconfig import Config

log = create_logger(Config().get("logging"))


class ORMWrapperServiceInstance(ORMWrapper):
    @property
    def serviceinstanceattribute_dict(self):
        attrs = {}
        for attr in self.service_instance_attributes.all():
            attrs[attr.name] = attr.value
        return attrs

    @property
    def westbound_service_instances(self):
        links = self.provided_links.all()
        instances = []
        for link in links:
            instances.append(link.subscriber_service_instance.leaf_model)

        return instances

    @property
    def eastbound_service_instances(self):
        links = self.subscribed_links.all()
        instances = []
        for link in links:
            instances.append(link.provider_service_instance.leaf_model)

        return instances

    def get_westbound_service_instance_properties(self, prop_name, include_self=False):
        if include_self and hasattr(self, prop_name):
            return getattr(self, prop_name)

        wi = self.westbound_service_instances

        if len(wi) == 0:
            log.error(
                "ServiceInstance with id %s has no westbound service instances, can't find property %s in the chain"
                % (self.id, prop_name)
            )
            raise Exception(
                "ServiceInstance with id %s has no westbound service instances"
                % self.id
            )

        for i in wi:
            if hasattr(i, prop_name):
                return getattr(i, prop_name)
            else:
                # cast to the ServiceInstance model
                i = self.stub.ServiceInstance.objects.get(id=i.id)
                return i.get_westbound_service_instance_properties(prop_name)


register_convenience_wrapper("ServiceInstance", ORMWrapperServiceInstance)
