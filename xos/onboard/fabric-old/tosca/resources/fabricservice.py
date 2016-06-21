import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from services.fabric.models import FabricService

from service import XOSService

class FabricService(XOSService):
    provides = "tosca.nodes.FabricService"
    xos_model = FabricService
    copyin_props = ["view_url", "icon_url", "enabled", "published", "public_key", "versionNumber"]

