import os
import base64
from netaddr import IPAddress, IPNetwork
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.slice import Slice, ControllerSlices
from util.logger import Logger, logging
from observer.steps.sync_controller_slices import *

logger = Logger(level=logging.INFO)

class SyncSlices(OpenStackSyncStep):
    provides=[Slice]
    requested_interval=0

    def sync_record(self, slice):
        for controller_slice in ControllerSlices.objects.filter(slice=slice):
            # bump the 'updated' timestamp and trigger observer to update
            # slice across all controllers 
            controller_slice.save()    

    def delete_record(self, slice):
        controller_slice_deleter = SyncControllerSlices().delete_record
        for controller_slice in ControllerSlices.objects.filter(slice=slice):
            try:
                controller_slice_deleter(controller_slice)
            except Exception,e:
                logger.log_exc("Failed to delete controller_slice %s" % controller_slice) 
                raise e
