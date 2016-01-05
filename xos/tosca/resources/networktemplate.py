import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from core.models import Slice,User,Network,NetworkTemplate

from xosresource import XOSResource

class XOSNetworkTemplate(XOSResource):
    provides = "tosca.nodes.NetworkTemplate"
    xos_model = NetworkTemplate
    copyin_props = ["visibility", "translation", "shared_network_name", "shared_network_id", "toplogy_kind", "controller_kind", "access"]

    def get_xos_args(self):
        args = super(XOSNetworkTemplate, self).get_xos_args()

        return args

    def create(self):
        nodetemplate = self.nodetemplate

        xos_args = self.get_xos_args()

        networkTemplate = NetworkTemplate(**xos_args)
        networkTemplate.caller = self.user
        networkTemplate.save()

        self.info("Created NetworkTemplate '%s' " % (str(networkTemplate), ))

    def delete(self, obj):
        if obj.network_set.exists():
            return

        super(XOSNetworkTemplate, self).delete(obj)



