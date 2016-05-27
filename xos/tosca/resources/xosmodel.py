import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from core.models import XOS

from xosresource import XOSResource

class XOSXOS(XOSResource):
    provides = "tosca.nodes.XOS"
    xos_model = XOS



