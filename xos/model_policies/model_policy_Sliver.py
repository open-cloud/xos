
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
