import os
import base64
from netaddr import IPAddress, IPNetwork
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.slice import Slice, SliceDeployments
from util.logger import Logger, logging

logger = Logger(level=logging.INFO)

class SyncSlices(OpenStackSyncStep):
    provides=[Slice]
    requested_interval=0

    def sync_record(self, slice):
        for slice_deployment in SliceDeployments.objects.filter(slice=slice):
            # bump the 'updated' timestamp and trigger observer to update
            # slice across all deployments 
            slice_deployment.save()    

    def delete_record(self, slice):
        slice_deployment_deleter = SliceDeploymentDeleter()
        for slice_deployment in SliceDeployments.objects.filter(slice=slice):
            try:
                slice_deployment_deleter(slice_deployment.id)
            except Exception,e:
                logger.log_exc("Failed to delete slice_deployment %s" % slice_deployment) 
                raise e
