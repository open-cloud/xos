import os
import base64
from netaddr import IPAddress, IPNetwork
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.slice import Slice
from util.logger import Logger, logging

logger = Logger(level=logging.INFO)

class SyncSlices(OpenStackSyncStep):
    provides=[Slice]
    requested_interval=0

    def fetch_pending(self):
        return Slice.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))

    def sync_record(self, slice):
        slice.save()
