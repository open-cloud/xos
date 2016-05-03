# note: this module named xossite.py instead of site.py due to conflict with
#    /usr/lib/python2.7/site.py

import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from core.models import User, Deployment, SliceRole

from xosresource import XOSResource

class XOSSliceRole(XOSResource):
    provides = "tosca.nodes.SliceRole"
    xos_model = SliceRole
    name_field = "role"

    def get_xos_args(self):
        args = super(XOSSliceRole, self).get_xos_args()

        return args

    def delete(self, obj):
        super(XOSSliceRole, self).delete(obj)



