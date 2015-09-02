import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate
import pdb

from core.models import Subscriber,User

from xosresource import XOSResource

class XOSSubscriber(XOSResource):
    provides = "tosca.nodes.Subscriber"
    xos_model = Subscriber
    copyin_props = ["service_specific_id"]

    def postprocess(self, obj):
        pass

    def can_delete(self, obj):
        return super(XOSService, self).can_delete(obj)

