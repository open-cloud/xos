
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
from core.models import Instance,User,Network,NetworkTemplate,Port

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



