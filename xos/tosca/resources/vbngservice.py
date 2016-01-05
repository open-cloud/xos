import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from services.cord.models import VBNGService

from service import XOSService

class XOSVBGNService(XOSService):
    provides = "tosca.nodes.VBNGService"
    xos_model = VBNGService
    copyin_props = ["view_url", "icon_url", "enabled", "published", "public_key", "versionNumber", "vbng_url"]

