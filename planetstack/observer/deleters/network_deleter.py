from core.models import Network
from observer.deleter import Deleter

class NetworkDeleter(Deleter):
    model='Network'

    def call(self, pk):
        network = Network.objects.get(pk=pk) 
        if (network.router_id) and (network.subnet_id):
            self.driver.delete_router_interface(network.router_id, network.subnet_id)
        if network.subnet_id:
            self.driver.delete_subnet(network.subnet_id)
        if network.router_id:
            self.driver.delete_router(network.router_id)
        if network.network_id:
            self.driver.delete_network(network.network_id)
        network.delete()
