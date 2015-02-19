from core.models import NetworkSliver
from observer.deleter import Deleter

class NetworkSliverDeleter(Deleter):
    model='NetworkSliver'

    def call(self, pk):
        network_sliver = NetworkSlivers.objects.get(pk=pk)
        # handle openstack delete

        network_sliver.delete() 

    
