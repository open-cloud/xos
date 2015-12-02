import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from cord.models import VCPEService

from service import XOSService

class XOSVcpeService(XOSService):
    provides = "tosca.nodes.VCPEService"
    xos_model = VCPEService
    copyin_props = ["view_url", "icon_url", "enabled", "published", "public_key", "private_key_fn", "versionNumber", "backend_network_label"]

