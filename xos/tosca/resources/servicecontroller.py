import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from core.models import ServiceController

from xosresource import XOSResource

class XOSServiceController(XOSResource):
    provides = "tosca.nodes.ServiceController"
    xos_model = ServiceController
    copyin_props = ["base_url"]



