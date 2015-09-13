import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from core.models import Instance,User,Network,NetworkTemplate,Port

from xosresource import XOSResource

class XOSPort(XOSResource):
    provides = ["tosca.nodes.network.Port"]
    xos_model = Port

    def get_existing_objs(self):
        # Port objects have no name, their unique key is (instance, network)
        args = self.get_xos_args(throw_exception=False)
        instance = args.get('instance',None)
        network = args.get('network',None)
        if (not instance) or (not network):
            return []
        return self.xos_model.objects.filter(**{'instance': instance, 'network': network})

    def get_xos_args(self, throw_exception=True):
        args = {}

        instance_name = self.get_requirement("tosca.relationships.network.BindsTo")
        if instance_name:
            args["instance"] = self.get_xos_object(Instance, throw_exception, name=instance_name)

        net_name = self.get_requirement("tosca.relationships.network.LinksTo")
        if net_name:
            args["network"] = self.get_xos_object(Network, throw_exception, name=net_name)

        return args

    def postprocess(self, obj):
        pass

    def create(self):
        xos_args = self.get_xos_args()

        if not xos_args.get("instance", None):
            raise Exception("Must specify slver when creating port")
        if not xos_args.get("network", None):
            raise Exception("Must specify network when creating port")

        port = Port(**xos_args)
        port.caller = self.user
        port.save()

        self.postprocess(port)

        self.info("Created Port '%s' connect instance '%s' to network %s" % (str(port), str(port.instance), str(port.network)))

    def delete(self, obj):
        super(XOSPort, self).delete(obj)



