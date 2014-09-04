import os
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.network import *
from util.logger import Logger, logging
from observer.steps.sync_network_deployments import *

logger = Logger(level=logging.INFO)

class SyncNetworks(OpenStackSyncStep):
    provides=[Network]
    requested_interval = 0

    def sync_record(self, network):
        network.save()

    def delete_record(self, network):
        network_deployment_deleter = SyncNetworkDeployments().delete_record
        for network_deployment in NetworkDeployments.objects.filter(network=network):
            try:
                network_deployment_deleter(network_deployment)    
            except Exeption,e:
                logger.log_exc("Failed to delete network deployment %s" % network_deployment)
                raise e
