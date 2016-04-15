import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from services.vrouter.models import VRouterService

from service import XOSService

class XOSVRouterService(XOSService):
    provides = "tosca.nodes.VRouterService"
    xos_model = VRouterService
    copyin_props = ["view_url", "icon_url", "enabled", "published", "public_key", "versionNumber"]

