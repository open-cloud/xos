
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

import logging as log

class ORMWrapperVOLTServiceInstance(ORMWrapper):

    @property
    def vsg(self):
        log.warning('VOLTServiceInstance.vsg is DEPRECATED, use get_westbound_service_instance_properties instead')
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
        log.warning('VOLTServiceInstance.vcpe is DEPRECATED, use VOLTServiceInstance.vsg instead')
        return self.vsg

    @property
    def subscriber(self):
        log.warning(
            'VOLTServiceInstance.subscriber is DEPRECATED, use get_westbound_service_instance_properties instead')
        # NOTE this assume that each VOLT has just 1 subscriber, is that right?
        links = self.stub.ServiceInstanceLink.objects.filter(provider_service_instance_id = self.id)
        for link in links:
            subs = self.stub.CordSubscriberRoot.objects.filter(id=link.subscriber_service_instance_id)
            if subs:
                return subs[0]
        return None

    @property
    def c_tag(self):
        log.warning(
            'VOLTServiceInstance.c_tag is DEPRECATED, use get_westbound_service_instance_properties instead')
        return self.subscriber.c_tag

    def get_olt_device_by_subscriber(self):
        si = self.stub.ServiceInstance.objects.get(id=self.id)

        olt_device_name = si.get_westbound_service_instance_properties("olt_device")

        olt_device = self.stub.OLTDevice.objects.get(name=olt_device_name)
        return olt_device

    def get_olt_port_by_subscriber(self):
        si = self.stub.ServiceInstance.objects.get(id=self.id)

        olt_port_name = si.get_westbound_service_instance_properties("olt_port")

        olt_device = self.get_olt_device_by_subscriber()
        olt_port = self.stub.PONPort.objects.get(name=olt_port_name, olt_device_id=olt_device.id)
        return olt_port

    @property
    def s_tag(self):
        try:
            olt_port = self.get_olt_port_by_subscriber()

            if olt_port:
                return olt_port.s_tag
            return None
        except Exception, e:
            log.warning('Error while reading s_tag: %s' % e.message)
            return None

    @property
    def switch_datapath_id(self):
        try:
            olt_device = self.get_olt_device_by_subscriber()
            if olt_device:
                return olt_device.switch_datapath_id
            return None
        except Exception, e:
            log.warning('Error while reading switch_datapath_id: %s' % e.message)
            return None

    @property
    def switch_port(self):
        try:
            olt_device = self.get_olt_device_by_subscriber()
            if olt_device:
                return olt_device.switch_port
            return None
        except Exception, e:
            log.warning('Error while reading switch_port: %s' % e.message)
            return None

    @property
    def outer_tpid(self):
        try:
            olt_device = self.get_olt_device_by_subscriber()
            if olt_device:
                return olt_device.outer_tpid
            return None
        except Exception, e:
            log.warning('Error while reading outer_tpid: %s' % e.message)
            return None


register_convenience_wrapper("VOLTServiceInstance", ORMWrapperVOLTServiceInstance)
