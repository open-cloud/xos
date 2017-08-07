
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


KIND="generic"

def __init__(self, *args, **kwargs):
    # for subclasses, set the default kind appropriately
    self._meta.get_field("kind").default = self.KIND
    super(Service, self).__init__(*args, **kwargs)

@property
def serviceattribute_dict(self):
    attrs = {}
    for attr in self.serviceattributes.all():
        attrs[attr.name] = attr.value
    return attrs

def get_scalable_nodes(self, slice, max_per_node=None, exclusive_slices=[]):
    """
         Get a list of nodes that can be used to scale up a slice.

            slice - slice to scale up
            max_per_node - maximum numbers of instances that 'slice' can have on a single node
            exclusive_slices - list of slices that must have no nodes in common with 'slice'.
    """

    # late import to get around order-of-imports constraint in __init__.py
    from core.models import Node, Instance

    nodes = list(Node.objects.all())

    conflicting_instances = Instance.objects.filter(
        slice__in=exclusive_slices)
    conflicting_nodes = Node.objects.filter(
        instances__in=conflicting_instances)

    nodes = [x for x in nodes if x not in conflicting_nodes]

    # If max_per_node is set, then limit the number of instances this slice
    # can have on a single node.
    if max_per_node:
        acceptable_nodes = []
        for node in nodes:
            existing_count = node.instances.filter(slice=slice).count()
            if existing_count < max_per_node:
                acceptable_nodes.append(node)
        nodes = acceptable_nodes

    return nodes

def pick_node(self, slice, max_per_node=None, exclusive_slices=[]):
    # Pick the best node to scale up a slice.

    nodes = self.get_scalable_nodes(slice, max_per_node, exclusive_slices)
    nodes = sorted(nodes, key=lambda node: node.instances.all().count())
    if not nodes:
        return None
    return nodes[0]

def adjust_scale(self, slice_hint, scale, max_per_node=None, exclusive_slices=[]):
    # late import to get around order-of-imports constraint in __init__.py
    from core.models import Instance

    slices = [x for x in self.slices.all() if slice_hint in x.name]
    for slice in slices:
        while slice.instances.all().count() > scale:
            s = slice.instances.all()[0]
            # print "drop instance", s
            s.delete()

        while slice.instances.all().count() < scale:
            node = self.pick_node(slice, max_per_node, exclusive_slices)
            if not node:
                # no more available nodes
                break

            image = slice.default_image
            if not image:
                raise XOSConfigurationError(
                    "No default_image for slice %s" % slice.name)

            flavor = slice.default_flavor
            if not flavor:
                raise XOSConfigurationError(
                    "No default_flavor for slice %s" % slice.name)

            s = Instance(slice=slice,
                         node=node,
                         creator=slice.creator,
                         image=image,
                         flavor=flavor,
                         deployment=node.site_deployment.deployment)
            s.save()

            # print "add instance", s

def get_vtn_src_nets(self):
    nets = []
    for slice in self.slices.all():
        for ns in slice.networkslices.all():
            if not ns.network:
                continue
#                if ns.network.template.access in ["direct", "indirect"]:
#                    # skip access networks; we want to use the private network
#                    continue
            if "management" in ns.network.name:
                # don't try to connect the management network to anything
                continue
            if ns.network.name in ["wan_network", "lan_network"]:
                # we don't want to attach to the vCPE's lan or wan network
                # we only want to attach to its private network
                # TODO: fix hard-coding of network name
                continue
            for cn in ns.network.controllernetworks.all():
                if cn.net_id:
                    net = {"name": ns.network.name, "net_id": cn.net_id}
                    nets.append(net)
    return nets

def get_vtn_nets(self):
    nets = []
    for slice in self.slices.all():
        for ns in slice.networkslices.all():
            if not ns.network:
                continue
            if ns.network.template.access not in ["direct", "indirect"]:
                # skip anything that's not an access network
                continue
            for cn in ns.network.controllernetworks.all():
                if cn.net_id:
                    net = {"name": ns.network.name, "net_id": cn.net_id}
                    nets.append(net)
    return nets

def get_vtn_dependencies_nets(self):
    provider_nets = []
    for tenant in self.subscribed_tenants.all():
        if tenant.provider_service:
            for net in tenant.provider_service.get_vtn_nets():
                if not net in provider_nets:
                    net["bidirectional"] = tenant.connect_method!="private-unidirectional"
                    provider_nets.append(net)
    return provider_nets

def get_vtn_dependencies_ids(self):
    return [x["net_id"] for x in self.get_vtn_dependencies_nets()]

def get_vtn_dependencies_names(self):
    return [x["name"] + "_" + x["net_id"] for x in self.get_vtn_dependencies_nets()]

def get_vtn_src_ids(self):
    return [x["net_id"] for x in self.get_vtn_src_nets()]

def get_vtn_src_names(self):
    return [x["name"] + "_" + x["net_id"] for x in self.get_vtn_src_nets()]

def get_composable_networks(self):
    SUPPORTED_VTN_SERVCOMP_KINDS = ['VSG','PRIVATE']

    nets = []
    for slice in self.slices.all():
        for net in slice.networks.all():
            if (net.template.vtn_kind not in SUPPORTED_VTN_SERVCOMP_KINDS) or (net.owner != slice):
                continue

            if not net.controllernetworks.exists():
                continue
            nets.append(net)
    return nets



