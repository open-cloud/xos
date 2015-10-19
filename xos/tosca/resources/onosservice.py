import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from services.onos.models import ONOSService

from service import XOSService

class XOSONOSService(XOSService):
    provides = "tosca.nodes.ONOSService"
    xos_model = ONOSService
    copyin_props = ["view_url", "icon_url", "enabled", "published", "public_key", "versionNumber"]

