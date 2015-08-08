import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from core.models import Slice,User,Site,Network,NetworkSlice,SliceRole,SlicePrivilege

from xosresource import XOSResource

class XOSSlice(XOSResource):
    provides = "tosca.nodes.Slice"
    xos_model = Slice

    def get_xos_args(self):
        site_name = self.get_requirement("tosca.relationships.MemberOfSite", throw_exception=True)
        site = self.get_xos_object(Site, login_base=site_name)
        return {"name": self.nodetemplate.name,
                "site": site}

    def postprocess(self, obj):
        for net_name in self.get_requirements("tosca.relationships.ConnectsToNetwork"):
            net = self.get_xos_object(Network, name=net_name)
            if not NetworkSlice.objects.filter(network=net, slice=obj):
                ns = NetworkSlice(network=net, slice=obj)
                ns.save()
                self.info("Added network connection from '%s' to '%s'" % (str(obj), str(net)))

        rolemap = ( ("tosca.relationships.AdminPrivilege", "admin"), ("tosca.relationships.AccessPrivilege", "access"),
                    ("tosca.relationships.PIPrivilege", "pi"), ("tosca.relationships.TechPrivilege", "tech") )
        for (rel, role) in rolemap:
            for email in self.get_requirements(rel):
                role = self.get_xos_object(SliceRole, role=role)
                user = self.get_xos_object(User, email=email)
                if not SlicePrivilege.objects.filter(user=user, role=role, slice=obj):
                    sp = SlicePrivilege(user=user, role=role, slice=obj)
                    sp.save()
                    self.info("Added slice privilege on %s role %s for %s" % (str(obj), str(role), str(user)))

    def create(self):
        nodetemplate = self.nodetemplate
        sliceName = nodetemplate.name

        xos_args = self.get_xos_args()
        slice = Slice(**xos_args)
        slice.caller = self.user
        slice.save()

        self.postprocess(slice)

        self.info("Created Slice '%s' on Site '%s'" % (str(slice), str(slice.site)))

    def delete(self, obj):
        if obj.slivers.exists():
            self.info("Slice %s has active slivers; skipping delete" % obj.name)
            return
        super(XOSSlice, self).delete(obj)



