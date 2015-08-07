import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from core.models import Slice,User,Network,NetworkTemplate

from xosresource import XOSResource

class XOSNetwork(XOSResource):
    provides = "tosca.nodes.XOSNetwork"
    xos_model = Network

    def get_xos_args(self):
        args = {"name": self.nodetemplate.name}

        slice_name = self.get_requirement("tosca.relationships.MemberOfSlice")
        if slice_name:
            args["owner"] = self.get_xos_object(Slice, name=slice_name)

        net_template_name = self.get_requirement("tosca.relationships.UsesNetworkTemplate")
        if net_template_name:
            args["template"] = self.get_xos_object(NetworkTemplate, name=net_template_name)

        # copy simple string properties from the template into the arguments
        for prop in ["ports", "labels", "permit_all_slices"]:
            v = self.get_property(prop)
            if v:
                args[prop] = v

        return args

    def postprocess(self, obj):
        v = self.get_property("permitted_slices")
        if v:
            for slicename in v.split(","):
                slice = self.get_xos_object(Slice, name = slicename.strip())

                if not obj.permitted_slices.filter(id = slice.id).exists():
                    obj.permitted_slices.add(slice)

    def create(self):
        nodetemplate = self.nodetemplate

        xos_args = self.get_xos_args()

        if not xos_args.get("owner", None):
            raise Exception("Must specify slice when creating network")
        if not xos_args.get("template", None):
            raise Exception("Must specify network template when creating network")

        network = Network(**xos_args)
        network.caller = self.user
        network.save()

        self.postprocess(network)

        self.info("Created Network '%s' owned by Slice '%s'" % (str(network), str(network.owner)))

    def delete(self, obj):
        super(XOSNetwork, self).delete(obj)



