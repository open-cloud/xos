import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate
import pdb

from core.models import User
from services.cord.models import CordSubscriberRoot

from xosresource import XOSResource

class XOSCORDUser(XOSResource):
    provides = "tosca.nodes.CORDUser"

    def get_model_class_name(self):
        return "CORDUser"

    def get_subscriber_root(self, throw_exception=True):
        sub_name = self.get_requirement("tosca.relationships.SubscriberDevice", throw_exception=throw_exception)
        sub = self.get_xos_object(CordSubscriberRoot, name=sub_name, throw_exception=throw_exception)
        return sub

    def get_existing_objs(self):
        result = []
        sub = self.get_subscriber_root(throw_exception=False)
        if not sub:
           return []
        for user in sub.users:
            if user["name"] == self.obj_name:
                result.append(user)
        return result

    def get_xos_args(self):
        args = {"name": self.obj_name,
                "level": self.get_property("level"),
                "mac": self.get_property("mac")}
        return args


    def create(self):
        xos_args = self.get_xos_args()
        sub = self.get_subscriber_root()

        sub.create_user(**xos_args)
        sub.save()

        self.info("Created CORDUser %s for Subscriber %s" % (self.obj_name, sub.name))

    def update(self, obj):
        pass

    def delete(self, obj):
        if (self.can_delete(obj)):
            self.info("destroying CORDUser %s" % obj["name"])
            sub = self.get_subscriber_root()
            sub.delete_user(obj["id"])
            sub.save()

    def can_delete(self, obj):
        return True

