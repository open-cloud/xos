import os
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.site import Site
from observer.steps.sync_controller_sites import *

class SyncSites(OpenStackSyncStep):
    provides=[Site]
    requested_interval=0

    def sync_record(self, site):
        site.save()

    def delete_record(self, site):
        controller_sites = ControllerSites.objects.filter(site=site)
        controller_site_deleter = SyncControllerSites().delete_record
        for controller_site in controller_sites:
            controller_site_deleter(controller_site)
