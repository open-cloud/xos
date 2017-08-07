
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


from __future__ import absolute_import

from core.models.xos import XOS
from core.models.xosbase import *
from django.core.validators import URLValidator
import urlparse
from operator import attrgetter
import json
from distutils.version import LooseVersion
from django.core.validators import URLValidator
from xos.exceptions import *


COARSE_KIND = "coarse"

def get_xos():
    xos = XOS.objects.all()

    if xos:
       return xos[0]
    else:
       return None

class AttributeMixin(object):
    # helper for extracting things from a json-encoded
    # service_specific_attribute

    def get_attribute(self, name, default=None):
        if self.service_specific_attribute:
            attributes = json.loads(self.service_specific_attribute)
        else:
            attributes = {}
        return attributes.get(name, default)

    def set_attribute(self, name, value):
        if self.service_specific_attribute:
            attributes = json.loads(self.service_specific_attribute)
        else:
            attributes = {}
        attributes[name] = value
        self.service_specific_attribute = json.dumps(attributes)

    def get_initial_attribute(self, name, default=None):
        if self._initial["service_specific_attribute"]:
            attributes = json.loads(
                self._initial["service_specific_attribute"])
        else:
            attributes = {}
        return attributes.get(name, default)

    @classmethod
    def get_default_attribute(cls, name):
        for (attrname, default) in cls.simple_attributes:
            if attrname == name:
                return default
        if hasattr(cls, "default_attributes"):
            if name in cls.default_attributes:
                return cls.default_attributes[name]

        return None

    @classmethod
    def setup_simple_attributes(cls):
        for (attrname, default) in cls.simple_attributes:
            setattr(cls, attrname, property(lambda self, attrname=attrname, default=default: self.get_attribute(attrname, default),
                                            lambda self, value, attrname=attrname: self.set_attribute(
                                                attrname, value),
                                            None,
                                            attrname))


class Scheduler(object):
    # XOS Scheduler Abstract Base Class
    # Used to implement schedulers that pick which node to put instances on

    def __init__(self, slice):
        self.slice = slice

    def pick(self):
        # this method should return a tuple (node, parent)
        #    node is the node to instantiate on
        #    parent is for container_vm instances only, and is the VM that will
        #      hold the container

        raise Exception("Abstract Base")


class LeastLoadedNodeScheduler(Scheduler):
    # This scheduler always return the node with the fewest number of
    # instances.

    def __init__(self, slice, label=None):
        super(LeastLoadedNodeScheduler, self).__init__(slice)
        self.label = label

    def pick(self):
        from core.models import Node

        # start with all nodes
        nodes = Node.objects.all()

        # if a label is set, then filter by label
        if self.label:
            nodes = nodes.filter(nodelabels__name=self.label)

        # if slice.default_node is set, then filter by default_node
        if self.slice.default_node:
            nodes = nodes.filter(name = self.slice.default_node)

        # convert to list
        nodes = list(nodes)

        # sort so that we pick the least-loaded node
        nodes = sorted(nodes, key=lambda node: node.instances.all().count())

        if not nodes:
            raise Exception(
                "LeastLoadedNodeScheduler: No suitable nodes to pick from")

        # TODO: logic to filter nodes by which nodes are up, and which
        #   nodes the slice can instantiate on.
#        nodes = sorted(nodes, key=lambda node: node.instances.all().count())
        return [nodes[0], None]


class ContainerVmScheduler(Scheduler):
    # This scheduler picks a VM in the slice with the fewest containers inside
    # of it. If no VMs are suitable, then it creates a VM.

    MAX_VM_PER_CONTAINER = 10

    def __init__(self, slice):
        super(ContainerVmScheduler, self).__init__(slice)

    @property
    def image(self):
        from core.models import Image

        # If slice has default_image set then use it
        if self.slice.default_image:
            return self.slice.default_image

        raise XOSProgrammingError("Please set a default image for %s" % self.slice.name)

    def make_new_instance(self):
        from core.models import Instance, Flavor

        flavors = Flavor.objects.filter(name="m1.small")
        if not flavors:
            raise XOSConfigurationError("No m1.small flavor")

        (node, parent) = LeastLoadedNodeScheduler(self.slice).pick()

        instance = Instance(slice=self.slice,
                            node=node,
                            image=self.image,
                            creator=self.slice.creator,
                            deployment=node.site_deployment.deployment,
                            flavor=flavors[0],
                            isolation="vm",
                            parent=parent)
        instance.save()
        # We rely on a special naming convention to identify the VMs that will
        # hole containers.
        instance.name = "%s-outer-%s" % (instance.slice.name, instance.id)
        instance.save()
        return instance

    def pick(self):
        from core.models import Instance, Flavor

        for vm in self.slice.instances.filter(isolation="vm"):
            avail_vms = []
            if (vm.name.startswith("%s-outer-" % self.slice.name)):
                container_count = Instance.objects.filter(parent=vm).count()
                if (container_count < self.MAX_VM_PER_CONTAINER):
                    avail_vms.append((vm, container_count))
            # sort by least containers-per-vm
            avail_vms = sorted(avail_vms, key=lambda x: x[1])
            print "XXX", avail_vms
            if avail_vms:
                instance = avail_vms[0][0]
                return (instance.node, instance)

        instance = self.make_new_instance()
        return (instance.node, instance)
