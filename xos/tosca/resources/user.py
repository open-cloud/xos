
# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from xosresource import XOSResource
from core.models import User, Site, SiteRole, SliceRole, SlicePrivilege, SitePrivilege

class XOSUser(XOSResource):
    provides = "tosca.nodes.User"
    xos_model = User
    name_field = "email"
    copyin_props = ["password", "firstname", "lastname", "phone", "user_url", "public_key", "is_active", "is_admin", "is_readonly", "is_appuser", "login_page"]

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
                    if not Privilege.objects.filter(accessor_id=obj.id, permission='role:'+role_obj.role, object_id=dest.id, accessor_type='User', object_type='Slice'):
                        sp = Privilege(accessor_id=obj.id, permission='role:'+role_obj.role, object_id=dest.id, accessor_type='User', object_type='Slice')
                        sp.save()
                        self.info("Added slice privilege on %s role %s for %s" % (str(dest), str(role), str(obj)))
                elif dest.__class__.__name__ == "Site":
                    role_obj = self.get_xos_object(SiteRole, role=role)
                    if not Privilege.objects.filter(accessor_id=obj.id, permission='role:'+role_obj.role, object_id=dest.id, accessor_type='User', object_type='Site'):
                        sp = SitePrivilege(accessor_id=obj.id, permission='role:'+role_obj.role, object_id=dest.id, accessor_type='User', object_type='Site')
                        sp.save()
                        self.info("Added site privilege on %s role %s for %s" % (str(dest), str(role), str(obj)))

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



