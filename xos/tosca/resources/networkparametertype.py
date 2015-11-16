import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from core.models import Slice,User,Network,NetworkParameterType

from xosresource import XOSResource

class XOSNetworkParameterType(XOSResource):
    provides = "tosca.nodes.NetworkParameterType"
    xos_model = NetworkParameterType
    copyin_props = []

    def get_xos_args(self):
        args = super(XOSNetworkParameterType, self).get_xos_args()

        return args

    def create(self):
        xos_args = self.get_xos_args()

        networkParameterType = NetworkParameterType(**xos_args)
        networkParameterType.caller = self.user
        networkParameterType.save()

        self.info("Created NetworkParameterType '%s' " % (str(networkParameterType), ))

    def delete(self, obj):
        if obj.networkparameters.exists():
            return

        super(XOSNetworkParameterType, self).delete(obj)



