import importlib
import os
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate
from django.contrib.contenttypes.models import ContentType

from core.models import Tag, Service

from xosresource import XOSResource

class XOSTag(XOSResource):
    provides = "tosca.nodes.Tag"
    xos_model = Tag
    name_field = None
    copyin_props = ("name", "value")

    def get_xos_args(self, throw_exception=True):
        args = super(XOSTag, self).get_xos_args()

        # Find the Tosca object that this Tag is pointing to, and return its
        # content_type and object_id, which will be used in the GenericForeignKey
        # django relation.

        target_name = self.get_requirement("tosca.relationships.TagsObject", throw_exception=throw_exception)
        if target_name:
            target_model = self.engine.name_to_xos_model(self.user, target_name)
            args["content_type"] = ContentType.objects.get_for_model(target_model)
            args["object_id"] = target_model.id

        service_name = self.get_requirement("tosca.relationships.MemberOfService", throw_exception=throw_exception)
        if service_name:
            args["service"] = self.get_xos_object(Service, name=service_name)

        # To uniquely identify a Tag, we must know the object that it is attached
        # to as well as the name of the Tag.

        if ("content_type" not in args) or ("object_id" not in args) or ("name" not in args):
           if throw_exception:
               raise Exception("Tag must specify TagsObject requirement and Name property")

        return args

    def get_existing_objs(self):
        args = self.get_xos_args(throw_exception=True)

        return Tag.objects.filter(content_type=args["content_type"],
                                  object_id=args["object_id"],
                                  name=args["name"])

    def postprocess(self, obj):
        pass

    def can_delete(self, obj):
        return super(XOSTag, self).can_delete(obj)

