import os
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.site import Site, SiteDeployments, ControllerSiteDeployments 
from observer.steps.sync_controller_site_deployments import *

class SyncSites(OpenStackSyncStep):
    provides=[Site]
    requested_interval=0

    def sync_record(self, site):
        site.save()

    def delete_record(self, site):
        # delete associated controllers site deployments
        ctrl_site_deployments = ControllerSiteDeployments.objects.filter(site_deployment__site=site)
        ctrl_site_deploy_deleter = SyncControllerSiteDeployments().delete_record
        for ctrl_site_deployment in ctrl_site_deployments:
            ctrl_site_deployment_deleter(ctrl_site_deployment)

        # delete site deployments
        site_deployments = SiteDeployments.objects.filter(site=site)
        for site_deployment in site_deployments:
            site_deployment.delete()    
         

	
