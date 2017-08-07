
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
from core.models import Slice,Instance,User,Flavor,Node,Image
from nodeselect import XOSNodeSelector
from imageselect import XOSImageSelector
from flavorselect import XOSFlavorSelector

class XOSCompute(XOSResource):
    provides = ["tosca.nodes.Compute", "tosca.nodes.Compute.Container"]
    xos_model = Instance

    def select_compute_node(self, user, v, hostname=None):
        mem_size = v.get_property_value("mem_size")
        num_cpus = v.get_property_value("num_cpus")
        disk_size = v.get_property_value("disk_size")

        flavor = XOSFlavorSelector(user, mem_size=mem_size, num_cpus=num_cpus, disk_size=disk_size).get_flavor()

        compute_node = XOSNodeSelector(user, mem_size=mem_size, num_cpus=num_cpus, disk_size=disk_size, hostname=hostname).get_nodes(1)[0]

        return (compute_node, flavor)

    def select_image(self, user, v):
        distribution = v.get_property_value("distribution")
        version = v.get_property_value("version")
        type = v.get_property_value("type")
        architecture = v.get_property_value("architecture")

        return XOSImageSelector(user, distribution=distribution, version=version, type=type, architecture=architecture).get_image()

    def get_xos_args(self, name=None, index=None):
        nodetemplate = self.nodetemplate

        if not name:
            name = self.obj_name

        args = {"name": name}

        host=None
        flavor=None
        image=None

        sliceName = self.get_requirement("tosca.relationships.MemberOfSlice", throw_exception=True)
        slice = self.get_xos_object(Slice, name=sliceName)

        # locate it one the same host as some other instance
        colocate_host = None
        colocate_instance_name = self.get_requirement("tosca.relationships.SameHost")
        if index is not None:
            colocate_instance_name = "%s-%d" % (colocate_instance_name, index)
        colocate_instances = Instance.objects.filter(name=colocate_instance_name)
        if colocate_instances:
            colocate_host = colocate_instances[0].node.name
            self.info("colocating on %s" % colocate_host)

        imageName = self.get_requirement("tosca.relationships.UsesImage", throw_exception=False)
        if imageName:
            image = self.get_xos_object(Image, name=imageName)

        capabilities = nodetemplate.get_capabilities()
        for (k,v) in capabilities.items():
            if (k=="host") and (not host):
                (compute_node, flavor) = self.select_compute_node(self.user, v, hostname=colocate_host)
            elif (k=="os") and (not image):
                image = self.select_image(self.user, v)

        if not compute_node:
            raise Exception("Failed to pick a host")
        if not image:
            raise Exception("Failed to pick an image")
        if not flavor:
            raise Exception("Failed to pick a flavor")

        args["image"] = image
        args["slice"] = slice
        args["flavor"] = flavor
        args["node"] = compute_node
        args["deployment"] = compute_node.site_deployment.deployment

        if nodetemplate.type == "tosca.nodes.Compute.Container":
            args["isolation"] = "container"

        return args

    def create(self, name = None, index = None):
        xos_args = self.get_xos_args(name=name, index=index)
        instance = Instance(**xos_args)
        instance.caller = self.user
        instance.no_sync = True
        instance.save()
        self.deferred_sync.append(instance)

        self.info("Created Instance '%s' on node '%s' using flavor '%s' and image '%s'" %
                  (str(instance), str(instance.node), str(instance.flavor), str(instance.image)))

    def create_or_update(self):
        scalable = self.get_scalable()

        if scalable.get("max_instances",1) > 1:
            for i in range(0, scalable.get("default_instances",1)):
                name = "%s-%d" % (self.obj_name, i)
                existing_instances = Instance.objects.filter(name=name)
                if existing_instances:
                    self.info("%s %s already exists" % (self.xos_model.__name__, name))
                    self.update(existing_instances[0])
                else:
                    self.create(name, index=i)
        else:
            super(XOSCompute,self).create_or_update()

    def get_existing_objs(self):
        scalable = self.get_scalable()

        if scalable.get("max_instances",1) > 1:
            existing_instances = []
            for i in range(0, scalable.get("default_instances",1)):
                name = "%s-%d" % (self.obj_name, i)
                existing_instances = existing_instances + list(Instance.objects.filter(name=name))
            return existing_instances
        else:
            return super(XOSCompute,self).get_existing_objs()

