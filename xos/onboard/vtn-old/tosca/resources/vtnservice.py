import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from services.vtn.models import VTNService

from service import XOSService

class XOSVTNService(XOSService):
    provides = "tosca.nodes.VTNService"
    xos_model = VTNService
    copyin_props = ["view_url", "icon_url", "enabled", "published", "public_key", "versionNumber", 'privateGatewayMac', 'localManagementIp', 'ovsdbPort', 'sshPort', 'sshUser', 'sshKeyFile', 'mgmtSubnetBits', 'xosEndpoint', 'xosUser', 'xosPassword']
