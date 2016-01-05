import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from services.hpc.models import HpcService

from service import XOSService

class XOSCdnService(XOSService):
    provides = "tosca.nodes.CDNService"
    xos_model = HpcService
    copyin_props = ["view_url", "icon_url"]

