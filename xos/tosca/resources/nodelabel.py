import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from core.models import NodeLabel

from xosresource import XOSResource

class XOSNodeLabel(XOSResource):
    provides = "tosca.nodes.NodeLabel"
    xos_model = NodeLabel

