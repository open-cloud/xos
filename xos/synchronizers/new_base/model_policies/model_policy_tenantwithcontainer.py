
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


from synchronizers.new_base.modelaccessor import *
from synchronizers.new_base.policy import Policy
from synchronizers.new_base.exceptions import *

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
        nodes = sorted(nodes, key=lambda node: node.instances.count())

        if not nodes:
            raise Exception(
                "LeastLoadedNodeScheduler: No suitable nodes to pick from")

        # TODO: logic to filter nodes by which nodes are up, and which
        #   nodes the slice can instantiate on.
        return [nodes[0], None]

class TenantWithContainerPolicy(Policy):
    model_name = None # This policy is abstract. Inherit this class into your own policy and override model_name

    def handle_create(self, tenant):
        return self.handle_update(tenant)

    def handle_update(self, tenant):
        self.manage_container(tenant)

#    def handle_delete(self, tenant):
#        if tenant.vcpe:
#            tenant.vcpe.delete()


    def save_instance(self, instance):
        # Override this function to do custom pre-save or post-save processing,
        # such as creating ports for containers.
        instance.save()

    def ip_to_mac(self, ip):
        (a, b, c, d) = ip.split('.')
        return "02:42:%02x:%02x:%02x:%02x" % (int(a), int(b), int(c), int(d))

    def allocate_public_service_instance(self, **kwargs):
        """ Get a ServiceInstance that provides public connectivity. Currently this means to use AddressPool and
            the AddressManager Service.

            Expect this to be refactored when we break hard-coded service dependencies.
        """
        address_pool_name = kwargs.pop("address_pool_name")

        am_service = AddressManagerService.objects.all()  # TODO: Hardcoded dependency
        if not am_service:
            raise Exception("no addressing services")
        am_service = am_service[0]

        ap = AddressPool.objects.filter(name=address_pool_name, service_id=am_service.id)
        if not ap:
            raise Exception("Addressing service unable to find addresspool %s" % name)
        ap = ap[0]

        ip = ap.get_address()
        if not ip:
            raise Exception("AddressPool '%s' has run out of addresses." % ap.name)

        ap.save()  # save the AddressPool to account for address being removed from it

        subscriber_service = None
        if "subscriber_service" in kwargs:
            subscriber_service = kwargs.pop("subscriber_service")

        subscriber_service_instance = None
        if "subscriber_tenant" in kwargs:
            subscriber_service_instance = kwargs.pop("subscriber_tenant")
        elif "subscriber_service_instance" in kwargs:
            subscriber_service_instance = kwargs.pop("subscriber_service_instance")

        # TODO: potential partial failure -- AddressPool address is allocated and saved before addressing tenant

        t = None
        try:
            t = AddressManagerServiceInstance(owner=am_service, **kwargs)    # TODO: Hardcoded dependency
            t.public_ip = ip
            t.public_mac = self.ip_to_mac(ip)
            t.address_pool_id = ap.id
            t.save()

            if subscriber_service:
                link = ServiceInstanceLink(subscriber_service = subscriber_service, provider_service_instance=t)
                link.save()

            if subscriber_service_instance:
                link = ServiceInstanceLink(subscriber_service_instance = subscriber_service_instance, provider_service_instance=t)
                link.save()
        except:
            # cleanup if anything went wrong
            ap.put_address(ip)
            ap.save()  # save the AddressPool to account for address being added to it
            if (t and t.id):
                t.delete()
            raise

        return t

    def get_image(self, tenant):
        slice = tenant.owner.slices.all()
        if not slice:
            raise SynchronizerProgrammingError("provider service has no slice")
        slice = slice[0]

        # If slice has default_image set then use it
        if slice.default_image:
            return slice.default_image

        raise SynchronizerProgrammingError("Please set a default image for %s" % self.slice.name)

    """ get_legacy_tenant_attribute
        pick_least_loaded_instance_in_slice
        count_of_tenants_of_an_instance

        These three methods seem to be used by A-CORD. Look for ways to consolidate with existing methods and eliminate
        these legacy ones
    """

    def get_legacy_tenant_attribute(self, tenant, name, default=None):
        if tenant.service_specific_attribute:
            attributes = json.loads(tenant.service_specific_attribute)
        else:
            attributes = {}
        return attributes.get(name, default)

    def pick_least_loaded_instance_in_slice(self, tenant, slices, image):
        for slice in slices:
            if slice.instances.all().count() > 0:
                for instance in slice.instances.all():
                    if instance.image != image:
                        continue
                    # Pick the first instance that has lesser than 5 tenants
                    if self.count_of_tenants_of_an_instance(tenant, instance) < 5:
                        return instance
        return None

    # TODO: Ideally the tenant count for an instance should be maintained using a
    # many-to-one relationship attribute, however this model being proxy, it does
    # not permit any new attributes to be defined. Find if any better solutions
    def count_of_tenants_of_an_instance(self, tenant, instance):
        tenant_count = 0
        for tenant in self.__class__.objects.all():
            if self.get_legacy_tenant_attribute(tenant, "instance_id", None) == instance.id:
                tenant_count += 1
        return tenant_count

    def manage_container(self, tenant):
        if tenant.deleted:
            return

        desired_image = self.get_image(tenant)

        if (tenant.instance is not None) and (tenant.instance.image.id != desired_image.id):
            tenant.instance.delete()
            tenant.instance = None

        if tenant.instance is None:
            if not tenant.owner.slices.count():
                raise SynchronizerConfigurationError("The service has no slices")

            new_instance_created = False
            instance = None
            if self.get_legacy_tenant_attribute(tenant, "use_same_instance_for_multiple_tenants", default=False):
                # Find if any existing instances can be used for this tenant
                slices = tenant.owner.slices.all()
                instance = self.pick_least_loaded_instance_in_slice(slices, desired_image)

            if not instance:
                slice = tenant.owner.slices.first()

                flavor = slice.default_flavor
                if not flavor:
                    flavors = Flavor.objects.filter(name="m1.small")
                    if not flavors:
                        raise SynchronizerConfigurationError("No m1.small flavor")
                    flavor = flavors[0]

                if slice.default_isolation == "container_vm":
                    raise Exception("Not implemented")
                else:
                    (node, parent) = LeastLoadedNodeScheduler(slice).pick()

                assert(slice is not None)
                assert(node is not None)
                assert(desired_image is not None)
                assert(tenant.creator is not None)
                assert(node.site_deployment.deployment is not None)
                assert(flavor is not None)

                try:
                    instance = Instance(slice=slice,
                                        node=node,
                                        image=desired_image,
                                        creator=tenant.creator,
                                        deployment=node.site_deployment.deployment,
                                        flavor=flavor,
                                        isolation=slice.default_isolation,
                                        parent=parent)
                    self.save_instance(instance)
                    new_instance_created = True

                    tenant.instance = instance
                    tenant.save()
                except:
                    # NOTE: We don't have transactional support, so if the synchronizer crashes and exits after
                    #       creating the instance, but before adding it to the tenant, then we will leave an
                    #       orphaned instance.
                    if new_instance_created:
                        instance.delete()
                    raise