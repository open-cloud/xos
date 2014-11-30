import os
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.network import *
from util.logger import Logger, logging
from observer.steps.sync_controller_networks import *

logger = Logger(level=logging.INFO)

class SyncNetworks(OpenStackSyncStep):
    provides=[Network]
    requested_interval = 0

    def sync_record(self, network):
        network.save()

    def delete_record(self, network):
        controller_networks_deleter = SyncControllerNetworks().delete_record
        for controller_network in ControllerNetworks.objects.filter(network=network):
            try:
                controller_network_deleter(controller_network)    
            except Exception,e:
                logger.log_exc("Failed to delete controller network %s" % controller_network)
                raise e
