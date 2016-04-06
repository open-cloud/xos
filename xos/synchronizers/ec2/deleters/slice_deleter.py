from core.models import Slice, SliceDeployments, User
from synchronizers.base.deleter import Deleter
from synchronizers.base.deleters.slice_deployment_deleter import SliceDeploymentsDeleter
from xos.logger import Logger, logging

logger = Logger(level=logging.INFO)

class SliceDeleter(Deleter):
    model='Slice'

    def call(self, pk):
        slice = Slice.objects.get(pk=pk)
        slice_deployment_deleter = SliceDeploymentsDeleter()
        for slice_deployment in SliceDeployments.objects.filter(slice=slice):
            try:
                slice_deployment_deleter(slice_deployment.id)
            except:
                logger.log_exc("Failed to delete slice_deployment %s" % slice_deployment,extra=slice.tologdict()) 
        slice.delete()
