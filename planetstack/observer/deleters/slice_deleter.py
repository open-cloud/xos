from core.models import Slice, SliceDeployments, User
from observer.deleter import Deleter
from observer.deleters.slice_deployment_deleter import SliceDeploymentDeleter
from util.logger import Logger, logging

logger = Logger(level=logging.INFO)

class SliceDeleter(Deleter):
    model='Slice'

    def call(self, pk):
        slice = Slice.objects.get(pk=pk)
        slice_deployment_deleter = SliceDeploymentDeleter()
        for slice_deployment in SliceDeployments.objects.filter(slice=slice):
            try:
                slice_deployment_deleter(slice_deployment.id)
            except:
                logger.log_exc("Failed to delete slice_deployment %s" % slice_deployment) 
        slice.delete()
