
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
from core.models import Tag, Service
from django.contrib.contenttypes.models import ContentType

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
            args["content_type"] = target_model.get_content_type_key()
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

