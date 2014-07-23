import os
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.site import Site

class SyncSites(OpenStackSyncStep):
    provides=[Site]
    requested_interval=0

    def sync_record(self, site):
        site.save()

    def delete_record(self, site):
        site_deployments = SiteDeployments.objects.filter(site=site)
        site_deployment_deleter = SiteDeploymentDeleter()
        for site_deployment in site_deployments:
            site_deployment_deleter(site_deployment.id)
