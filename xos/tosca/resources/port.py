import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from core.models import Sliver,User,Network,NetworkTemplate,NetworkSliver

from xosresource import XOSResource

class XOSPort(XOSResource):
    provides = ["tosca.nodes.network.Port"]
    xos_model = NetworkSliver

    def get_existing_objs(self):
        # Port objects have no name, their unique key is (sliver, network)
        args = self.get_xos_args(throw_exception=False)
        sliver = args.get('sliver',None)
        network = args.get('network',None)
        if (not sliver) or (not network):
            return []
        return self.xos_model.objects.filter(**{'sliver': sliver, 'network': network})

    def get_xos_args(self, throw_exception=True):
        args = {}

        sliver_name = self.get_requirement("tosca.relationships.network.BindsTo")
        if sliver_name:
            args["sliver"] = self.get_xos_object(Sliver, throw_exception, name=sliver_name)

        net_name = self.get_requirement("tosca.relationships.network.LinksTo")
        if net_name:
            args["network"] = self.get_xos_object(Network, throw_exception, name=net_name)

        return args

    def postprocess(self, obj):
        pass

    def create(self):
        xos_args = self.get_xos_args()

        if not xos_args.get("sliver", None):
            raise Exception("Must specify slver when creating port")
        if not xos_args.get("network", None):
            raise Exception("Must specify network when creating port")

        port = NetworkSliver(**xos_args)
        port.caller = self.user
        port.save()

        self.postprocess(port)

        self.info("Created NetworkSliver '%s' connect sliver '%s' to network %s" % (str(port), str(port.sliver), str(port.network)))

    def delete(self, obj):
        super(XOSPort, self).delete(obj)



