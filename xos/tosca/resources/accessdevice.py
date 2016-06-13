import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from services.volt.models import AccessDevice, VOLTDevice
from xosresource import XOSResource

class XOSAccessDevice(XOSResource):
    provides = "tosca.nodes.AccessDevice"
    xos_model = AccessDevice
    copyin_props = ["uplink", "vlan"]
    name_field = None

    def get_xos_args(self, throw_exception=True):
        args = super(XOSAccessDevice, self).get_xos_args()

        volt_device_name = self.get_requirement("tosca.relationships.MemberOfDevice", throw_exception=throw_exception)
        if volt_device_name:
            args["volt_device"] = self.get_xos_object(VOLTDevice, throw_exception=throw_exception, name=volt_device_name)

        return args

    # AccessDevice has no name field, so we rely on matching the keys. We assume
    # the for a given VOLTDevice, there is only one AccessDevice per (uplink, vlan)
    # pair.

    def get_existing_objs(self):
        args = self.get_xos_args(throw_exception=False)
        volt_device = args.get("volt_device", None)
        uplink = args.get("uplink", None)
        vlan = args.get("vlan", None)
        if (volt_device is not None) and (uplink is not None) and (vlan is not None):
            existing_obj = self.get_xos_object(AccessDevice, volt_device=volt_device, uplink=uplink, vlan=vlan, throw_exception=False)
            if existing_obj:
                return [ existing_obj ]
        return []

