import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from services.volt.models import AccessAgent, VOLTDevice, VOLTService, AgentPortMapping
from xosresource import XOSResource

class XOSAccessAgent(XOSResource):
    provides = "tosca.nodes.AccessAgent"
    xos_model = AccessAgent
    copyin_props = ["mac"]

    def get_xos_args(self, throw_exception=True):
        args = super(XOSAccessAgent, self).get_xos_args()

        volt_service_name = self.get_requirement("tosca.relationships.MemberOfService", throw_exception=throw_exception)
        if volt_service_name:
            args["volt_service"] = self.get_xos_object(VOLTService, throw_exception=throw_exception, name=volt_service_name)

        return args

    def postprocess(self, obj):
        # For convenient, allow the port mappings to be specified by a Tosca
        # string with commas between lines.
        #      <port> <mac>,
        #      <port> <mac>,
        #      ...
        #      <port> <mac>

        port_mappings_str = self.get_property("port_mappings")
        port_mappings = []
        if port_mappings_str:
            lines = [x.strip() for x in port_mappings_str.split(",")]
            for line in lines:
                if not (" " in line):
                    raise "Malformed port mapping `%s`", line
                (port, mac) = line.split(" ")
                port=port.strip()
                mac=mac.strip()
                port_mappings.append( (port, mac) )

            for apm in list(AgentPortMapping.objects.filter(access_agent=obj)):
                if (apm.port, apm.mac) not in port_mappings:
                    print "Deleting AgentPortMapping '%s'" % apm
                    apm.delete()

            for port_mapping in port_mappings:
                existing_objs = AgentPortMapping.objects.filter(access_agent=obj, port=port_mapping[0], mac=port_mapping[1])
                if not existing_objs:
                    apm = AgentPortMapping(access_agent=obj, port=port_mapping[0], mac=port_mapping[1])
                    apm.save()
                    print "Created AgentPortMapping '%s'" % apm

