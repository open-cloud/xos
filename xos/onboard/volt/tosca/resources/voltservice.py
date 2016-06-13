import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from services.volt.models import VOLTService

from service import XOSService

class XOSVOLTService(XOSService):
    provides = "tosca.nodes.VOLTService"
    xos_model = VOLTService
    copyin_props = ["view_url", "icon_url", "kind", "enabled", "published", "public_key", "private_key_fn", "versionNumber"]
