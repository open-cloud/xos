from core.models import Network, NetworkDeployments
from synchronizers.base.deleter import Deleter
from synchronizers.base.deleters.network_deployment_deleter import NetworkDeploymentDeleter
from xos.logger import Logger, logging

logger = Logger(level=logging.INFO)

class NetworkDeleter(Deleter):
    model='Network'

    def call(self, pk):
        network = Network.objects.get(pk=pk) 
        network_deployment_deleter = NetworkDeploymentDeleter()
        for network_deployment in NetworkDeployments.objects.filter(network=network):
            try:
                network_deployment_deleter(network_deployment.id)    
            except:
                logger.log_exc("Failed to delete network deployment %s" % network_deployment,extra=network.tologdict())
        network.delete()
