from core.models import Network, NetworkDeployments
from synchronizers.base.deleter import Deleter
from openstack.driver import OpenStackDriver

class NetworkDeploymentDeleter(Deleter):
    model='NetworkDeployment'

    def call(self, pk):
        network_deployment = NetworkDeployments.objects.get(pk=pk)
        driver = OpenStackDriver().client_driver(caller=network_deployment.network.owner.creator,
                                                 tenant=network_deployment.network.owner.name,
                                                 deployment=network_deployment.deployment.name)
        if (network_deployment.router_id) and (network_deployment.subnet_id):
            driver.delete_router_interface(network_deployment.router_id, network_deployment.subnet_id)
        if network_deployment.subnet_id:
            driver.delete_subnet(network_deployment.subnet_id)
        if network_deployment.router_id:
            driver.delete_router(network_deployment.router_id)
        if network_deployment.net_id:
            driver.delete_network(network_deployment.net_id)
        network_deployment.delete()
