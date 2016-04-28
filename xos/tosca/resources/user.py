import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate

from core.models import User, Site, SiteRole, SliceRole, SlicePrivilege, SitePrivilege, DashboardView, UserDashboardView

from xosresource import XOSResource

class XOSUser(XOSResource):
    provides = "tosca.nodes.User"
    xos_model = User
    name_field = "email"
    copyin_props = ["password", "firstname", "lastname", "phone", "user_url", "public_key", "is_active", "is_admin", "login_page"]

    def get_xos_args(self):
        args = super(XOSUser, self).get_xos_args()

        site_name = self.get_requirement("tosca.relationships.MemberOfSite")
        if site_name:
            args["site"] = self.get_xos_object(Site, login_base=site_name)

        return args

    def get_existing_objs(self):
        return self.xos_model.objects.filter(email = self.obj_name)

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

        dashboard_order = 10
        for reqs in self.nodetemplate.requirements:
            for (k,v) in reqs.items():
                if (v["relationship"] == "tosca.relationships.UsesDashboard"):
                    dashboard_name = v["node"]
                    dashboard = self.get_xos_object(DashboardView, name=dashboard_name)

                    udvs = UserDashboardView.objects.filter(user=obj, dashboardView=dashboard)
                    if not udvs:
                        self.info("Adding UserDashboardView from %s to %s" % (obj, dashboard))

                        udv = UserDashboardView(user=obj, dashboardView=dashboard, order=dashboard_order)
                        dashboard_order += 10
                        udv.save()

    def create(self):
        xos_args = self.get_xos_args()

        if not xos_args.get("site",None):
             raise Exception("Site name must be specified when creating user")
        if ("firstname" not in xos_args) or ("lastname" not in xos_args):
             raise Exception("firstname and lastname must be specified when creating user")

        user = User(**xos_args)
        user.save()

        self.postprocess(user)

        self.info("Created User '%s'" % (str(user), ))

    def update(self, obj):
        xos_args = self.get_xos_args()

        password = None
        if "password" in xos_args:
            # password needs to be set with set_password function
            password = xos_args["password"]
            del xos_args["password"]

        for (k,v) in xos_args.items():
            setattr(obj, k, v)

        if password:
            obj.set_password(password)

        self.postprocess(obj)
        obj.save()

    def delete(self, obj):
        if obj.slices.exists():
            self.info("User %s has active slices; skipping delete" % obj.name)
            return
        super(XOSUser, self).delete(obj)



