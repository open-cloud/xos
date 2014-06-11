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

    def fetch_pending(self):
        return Network.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))

    def sync_record(self, network):
        network.save()

