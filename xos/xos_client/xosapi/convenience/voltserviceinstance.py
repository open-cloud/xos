
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


from xosapi.orm import ORMWrapper, register_convenience_wrapper

class ORMWrapperVOLTServiceInstance(ORMWrapper):
    @property
    def vsg(self):
        links = self.stub.ServiceInstanceLink.objects.filter(subscriber_service_instance_id = self.id)
        for link in links:
            # cast from ServiceInstance to VSGTenant
            vsgs = self.stub.VSGServiceInstance.objects.filter(id = link.provider_service_instance.id)
            if vsgs:
                return vsgs[0]
        return None

    # DEPRECATED
    @property
    def vcpe(self):
        self.logger.warning('VOLTServiceInstance.vcpe is DEPRECATED, use VOLTServiceInstance.vsg instead')
        return self.vsg

    @property
    def subscriber(self):
        # NOTE this assume that each VOLT has just 1 subscriber, is that right?
        links = self.stub.ServiceInstanceLink.objects.filter(provider_service_instance_id = self.id)
        for link in links:
            subs = self.stub.CordSubscriberRoot.objects.filter(id=link.subscriber_service_instance_id)
            if subs:
                return subs[0]
        return None

    @property
    def c_tag(self):
        return self.subscriber.c_tag

    @property
    def s_tag(self):
        return self.subscriber.s_tag

register_convenience_wrapper("VOLTServiceInstance", ORMWrapperVOLTServiceInstance)
