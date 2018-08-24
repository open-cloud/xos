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


from xosapi.orm import ORMWrapper, register_convenience_wrapper

from xosconfig import Config
from multistructlog import create_logger

log = create_logger(Config().get('logging'))

class ORMWrapperServiceInstance(ORMWrapper):

    @property
    def serviceinstanceattribute_dict(self):
        attrs = {}
        for attr in self.service_instance_attributes.all():
            attrs[attr.name] = attr.value
        return attrs

    @property
    def tenantattribute_dict(self):
        log.warn("tenantattribute_dict method is deprecated")
        return self.serviceinstanceattribute_dict

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

    def create_eastbound_instance(self):

        # Already has a chain
        if len(self.eastbound_service_instances) > 0 and not self.is_new:
            log.debug("MODEL_POLICY: Subscriber %s is already part of a chain" % si.id)
            return

        # if it does not have a chain,
        # Find links to the next element in the service chain
        # and create one

        links = self.owner.subscribed_dependencies.all()

        for link in links:
            si_class = link.provider_service.get_service_instance_class_name()
            log.info(" %s creating %s" % (self.model_name, si_class))

            eastbound_si_class = model_accessor.get_model_class(si_class)
            eastbound_si = eastbound_si_class()
            eastbound_si.owner_id = link.provider_service_id
            eastbound_si.save()
            link = ServiceInstanceLink(provider_service_instance=eastbound_si, subscriber_service_instance=si)
            link.save()

    def get_westbound_service_instance_properties(self, prop_name, include_self=False):
        if include_self and hasattr(self, prop_name):
            return getattr(self, prop_name)

        wi = self.westbound_service_instances

        if len(wi) == 0:
            log.error("ServiceInstance with id %s has no westbound service instances, can't find property %s in the chain" % (self.id, prop_name))
            raise Exception("ServiceInstance with id %s has no westbound service instances" % self.id)

        for i in wi:
            if hasattr(i, prop_name):
                return getattr(i, prop_name)
            else:
                # cast to the ServiceInstance model
                i = self.stub.ServiceInstance.objects.get(id=i.id)
                return i.get_westbound_service_instance_properties(prop_name)

register_convenience_wrapper("ServiceInstance", ORMWrapperServiceInstance)