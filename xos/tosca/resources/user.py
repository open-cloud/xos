import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from core.models import User, Site, SiteRole, SliceRole, SlicePrivilege, SitePrivilege

from xosresource import XOSResource

class XOSUser(XOSResource):
    provides = "tosca.nodes.User"
    xos_model = User

    def get_xos_args(self):
        args = {"email": self.nodetemplate.name}

        # copy simple string properties from the template into the arguments
        for prop in ["password", "firstname", "lastname", "phone", "user_url", "public_key", "is_active", "is_admin", "login_page"]:
            v = self.get_property(prop)
            if v:
                args[prop] = v

        site_name = self.get_requirement("tosca.relationships.MemberOfSite")
        if site_name:
            args["site"] = self.get_xos_object(Site, login_base=site_name)

        return args

    def get_existing_objs(self):
        return self.xos_model.objects.filter(email = self.nodetemplate.name)

    def postprocess(self, obj):
        rolemap = ( ("tosca.relationships.AdminPrivilege", "admin"), ("tosca.relationships.AccessPrivilege", "access"),
                    ("tosca.relationships.PIPrivilege", "pi"), ("tosca.relationships.TechPrivilege", "tech") )
        for (rel, role) in rolemap:
            for obj_name in self.get_requirements(rel):
                dest = self.engine.name_to_xos_model(self.user, obj_name)
                if dest.__class__.__name__ == "Slice":
                    role_obj = self.get_xos_object(SliceRole, role=role)
                    if not SlicePrivilege.objects.filter(user=user, role=role_obj, slice=dest):
                        sp = SlicePrivilege(user=obj, role=role_obj, slice=dest)
                        sp.save()
                        self.info("Added slice privilege on %s role %s for %s" % (str(dest), str(role), str(obj)))
                elif dest.__class__.__name__ == "Site":
                    role_obj = self.get_xos_object(SiteRole, role=role)
                    if not SitePrivilege.objects.filter(user=obj, role=role_obj, site=dest):
                        sp = SitePrivilege(user=obj, role=role_obj, site=dest)
                        sp.save()
                        self.info("Added site privilege on %s role %s for %s" % (str(dest), str(role), str(obj)))

    def create(self):
        nodetemplate = self.nodetemplate

        xos_args = self.get_xos_args()

        if not xos_args.get("site",None):
             raise Exception("Site name must be specified when creating user")

        user = User(**xos_args)
        user.save()

        self.postprocess(user)

        self.info("Created User '%s'" % (str(user), ))

    def delete(self, obj):
        if obj.slices.exists():
            self.info("User %s has active slices; skipping delete" % obj.name)
            return
        super(XOSUser, self).delete(obj)



