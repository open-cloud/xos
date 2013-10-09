from core.models import Sliver
from observer.deleter import Deleter

class SliverDeleter(Deleter):
    model='Sliver'

    def call(self, pk):
        sliver = Sliver.objects.get(pk=pk)
        if sliver.instance_id:
            self.driver.destroy_instance(sliver.instance_id)
        sliver.delete()
