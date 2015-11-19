def handle_container_on_metal(instance):
        from core.models import Instance, Flavor, Port, Image

        if instance.deleted:
            return

        # Our current docker network strategy requires that there be some
        # VM on the server that connects to the networks, so that
        # the containers can piggyback off of that configuration.
        if not Instance.objects.filter(slice=instance.slice, node=instance.node, isolation="vm").exists():
            flavors = Flavor.objects.filter(name="m1.small")
            if not flavors:
                raise XOSConfigurationError("No m1.small flavor")

            images = Image.objects.filter(kind="vm")

            companion_instance = Instance(slice = instance.slice,
                            node = instance.node,
                            image = images[0],
                            creator = instance.creator,
                            deployment = instance.node.site_deployment.deployment,
                            flavor = flavors[0])
            companion_instance.save()

        # Add the ports for the container
        for network in instance.slice.networks.all():
            if (network.name.endswith("-nat")):
                continue

            if not Port.objects.filter(network=network, instance=instance).exists():
                port = Port(network = network, instance=instance)
                port.save()

def handle(instance):
    from core.models import Controller, ControllerSlice, ControllerNetwork, NetworkSlice

    networks = [ns.network for ns in NetworkSlice.objects.filter(slice=instance.slice)]
    controller_networks = ControllerNetwork.objects.filter(network__in=networks,
                                                                controller=instance.node.site_deployment.controller)

    for cn in controller_networks:
        if (cn.lazy_blocked):
		cn.lazy_blocked=False
		cn.backend_register = '{}'
		cn.save()

    if (instance.isolation in ["container", "container_vm"]):
        handle_container_on_metal(instance)
