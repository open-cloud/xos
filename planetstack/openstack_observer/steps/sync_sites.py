import os
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.site import Site, SiteDeployments, SiteDeployments 
from observer.steps.sync_controller_site_deployments import *

class SyncSites(OpenStackSyncStep):
    provides=[Site]
    requested_interval=0

    def sync_record(self, site):
        site.save()

    def delete_record(self, site):
        # delete associated controllers site deployments
        site_deployments = SiteDeployments.objects.filter(site=site)
        site_deploy_deleter = SyncControllerSiteDeployments().delete_record
        for site_deployment in site_deployments:
            site_deployment_deleter(site_deployment)

         

	
