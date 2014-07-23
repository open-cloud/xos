import os
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.network import *
from util.logger import Logger, logging

logger = Logger(level=logging.INFO)

class SyncNetworks(OpenStackSyncStep):
    provides=[Network]
    requested_interval = 0

    def fetch_pending(self, deleted):
        if (not deleted):
            objs = Network.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))
        else:
            objs = Network.deleted_objects.all()

    def sync_record(self, network):
        network.save()

    def delete_record(self, network):
        network_deployment_deleter = NetworkDeploymentDeleter()
        for network_deployment in NetworkDeployments.objects.filter(network=network):
            try:
                network_deployment_deleter(network_deployment.id)    
            except Exeption,e:
                logger.log_exc("Failed to delete network deployment %s" % network_deployment)
                raise e
        network.delete()
