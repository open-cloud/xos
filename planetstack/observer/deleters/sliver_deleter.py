from core.models import Sliver, SliceDeployments
from observer.deleter import Deleter

class SliverDeleter(Deleter):
    model='Sliver'

    def call(self, pk):
        sliver = Sliver.objects.get(pk=pk)
        if sliver.instance_id:
            driver = self.driver.client_driver(caller=sliver.creator, 
                                               tenant=sliver.slice.name,
                                               deployment=sliver.deploymentNetwork.name)
            driver.destroy_instance(sliver.instance_id)
        sliver.delete()
