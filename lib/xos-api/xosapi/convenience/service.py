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

from __future__ import absolute_import

from xosapi.orm import ORMWrapper, register_convenience_wrapper


class ORMWrapperService(ORMWrapper):
    @property
    def serviceattribute_dict(self):
        attrs = {}
        for attr in self.serviceattributes.all():
            attrs[attr.name] = attr.value
        return attrs

    def get_composable_networks(self):
        SUPPORTED_VTN_SERVCOMP_KINDS = ["VSG", "PRIVATE"]

        nets = []
        for slice in self.slices.all():
            for net in slice.networks.all():
                if (net.template.vtn_kind not in SUPPORTED_VTN_SERVCOMP_KINDS) or (
                    net.owner.id != slice.id
                ):
                    continue

                if not net.controllernetworks.exists():
                    continue
                nets.append(net)
        return nets

    def get_service_instance_class_name(self):
        # This assumes that a ServiceInstance is always named after its service. For example
        # VSGService --> VSGServiceInstance. Services in which this is not the case should override this method.
        # TODO: Specify via xproto ?
        return self.leaf_model_name + "Instance"

    def get_service_instance_class(self):
        return getattr(self.stub, self.get_service_instance_class_name())

    @property
    def provider_services(self):
        svcs = []
        service_deps = self.subscribed_dependencies.all()
        for dep in service_deps:
            svcs.append(dep.provider_service)
        return svcs

    @property
    def subscriber_services(self):
        svcs = []
        service_deps = self.provided_dependencies.all()
        for dep in service_deps:
            svcs.append(dep.subscriber_service)
        return svcs

    def acquire_service_instance(self, subscriber_service_instance):
        """ Given a subscriber_service_instance:
              1) If there is an eligible provider_service_instance that can be used, then link to it
              2) Otherwise, create a new provider_service_instance and link to it.

            This is the base class, knows nothing of service specifics, so it assumes that #1 always yields no
            eligible provider_service_instances. To get custom behavior, override this method in your own
            convenience wrapper.
        """
        si_classname = self.get_service_instance_class_name()

        ServiceInstanceLink = self.stub.ServiceInstanceLink

        eastbound_si_class = getattr(self.stub, si_classname)
        eastbound_si = eastbound_si_class(owner_id=self.id)
        eastbound_si.save()

        link = ServiceInstanceLink(
            provider_service_instance=eastbound_si,
            subscriber_service_instance=subscriber_service_instance,
        )
        link.save()

    def validate_links(self, subscriber_service_instance):
        """ Validate existing links between the provider and subscriber service instances. If a valid link exists,
            then return it. Return [] otherwise.

            This is the base class, knows nothing of service specifics, so it assumes that all existing links are
            valid. To get custom behavior, override this method in your own convenience wrapper.
        """
        matched = []
        for link in subscriber_service_instance.subscribed_links.all():
            if link.provider_service_instance.owner.id == self.id:
                matched.append(link.provider_service_instance.leaf_model)
        return matched


register_convenience_wrapper("Service", ORMWrapperService)
