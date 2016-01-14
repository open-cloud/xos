from core.models import Instance, SliceDeployments
from synchronizers.base.deleter import Deleter

class InstanceDeleter(Deleter):
    model='Instance'

    def call(self, pk):
        instance = Instance.objects.get(pk=pk)
        if instance.instance_id:
            driver = self.driver.client_driver(caller=instance.creator, 
                                               tenant=instance.slice.name,
                                               deployment=instance.deploymentNetwork.name)
            driver.destroy_instance(instance.instance_id)
        instance.delete()
