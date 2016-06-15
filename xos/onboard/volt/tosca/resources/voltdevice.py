import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from services.volt.models import VOLTDevice, VOLTService, AccessDevice, AccessAgent
from xosresource import XOSResource

class XOSVOLTDevice(XOSResource):
    provides = "tosca.nodes.VOLTDevice"
    xos_model = VOLTDevice
    copyin_props = ["openflow_id", "driver"]

    def get_xos_args(self, throw_exception=True):
        args = super(XOSVOLTDevice, self).get_xos_args()

        volt_service_name = self.get_requirement("tosca.relationships.MemberOfService", throw_exception=throw_exception)
        if volt_service_name:
            args["volt_service"] = self.get_xos_object(VOLTService, throw_exception=throw_exception, name=volt_service_name)

        agent_name = self.get_requirement("tosca.relationships.UsesAgent", throw_exception=throw_exception)
        if agent_name:
            args["access_agent"] = self.get_xos_object(AccessAgent, throw_exception=throw_exception, name=agent_name)

        return args

    def postprocess(self, obj):
        access_devices_str = self.get_property("access_devices")
        access_devices = []
        if access_devices_str:
            lines = [x.strip() for x in access_devices_str.split(",")]
            for line in lines:
                if not (" " in line):
                    raise "Malformed access device `%s`", line
                (uplink, vlan) = line.split(" ")
                uplink=int(uplink.strip())
                vlan=int(vlan.strip())
                access_devices.append( (uplink, vlan) )

            for ad in list(AccessDevice.objects.filter(volt_device=obj)):
                if (ad.uplink, ad.vlan) not in access_devices:
                    print "Deleting AccessDevice '%s'" % ad
                    ad.delete()

            for access_device in access_devices:
                existing_objs = AccessDevice.objects.filter(volt_device=obj, uplink=access_device[0], vlan=access_device[1])
                if not existing_objs:
                    ad = AccessDevice(volt_device=obj, uplink=access_device[0], vlan=access_device[1])
                    ad.save()
                    print "Created AccessDevice '%s'" % ad
