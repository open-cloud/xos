from synchronizers.new_base.modelaccessor import *
from synchronizers.new_base.policy import Policy

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

    def get_image(self, tenant):
        slice = tenant.provider_service.slices.all()
        if not slice:
            raise XOSProgrammingError("provider service has no slice")
        slice = slice[0]

        # If slice has default_image set then use it
        if slice.default_image:
            return slice.default_image

        raise XOSProgrammingError("Please set a default image for %s" % self.slice.name)

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
            if not tenant.provider_service.slices.count():
                raise XOSConfigurationError("The service has no slices")

            new_instance_created = False
            instance = None
            if self.get_legacy_tenant_attribute(tenant, "use_same_instance_for_multiple_tenants", default=False):
                # Find if any existing instances can be used for this tenant
                slices = tenant.provider_service.slices.all()
                instance = self.pick_least_loaded_instance_in_slice(slices, desired_image)

            if not instance:
                slice = tenant.provider_service.slices.first()

                flavor = slice.default_flavor
                if not flavor:
                    flavors = Flavor.objects.filter(name="m1.small")
                    if not flavors:
                        raise XOSConfigurationError("No m1.small flavor")
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