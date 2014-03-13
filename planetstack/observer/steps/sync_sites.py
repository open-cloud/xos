import os
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.site import Site

class SyncSites(OpenStackSyncStep):
    provides=[Site]
    requested_interval=0

    def fetch_pending(self):
        return Site.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))

    def sync_record(self, site):
        site.save()

