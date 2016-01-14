from core.models import NetworkInstance
from synchronizers.base.deleter import Deleter

class NetworkInstanceDeleter(Deleter):
    model='NetworkInstance'

    def call(self, pk):
        network_instance = NetworkInstances.objects.get(pk=pk)
        # handle openstack delete

        network_instance.delete() 

    
