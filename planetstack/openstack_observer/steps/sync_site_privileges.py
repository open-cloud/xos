import os
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models import User, UserDeployment, SitePrivilege, SiteDeployments   

class SyncSitePrivileges(OpenStackSyncStep):
    requested_interval=0
    provides=[SitePrivilege]

    def fetch_pending(self, deleted):
        # Deleting site privileges is not supported yet
        if (deleted):
            return []

        return SitePrivilege.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))

    def sync_record(self, site_priv):
        # sync site privileges at all site deployments
        site_deployments = SiteDeployments.objects.filter(site=site_priv.site)
        for site_deployment in site_deployments:
            user_deployments = UserDeployment.objects.filter(deployment=site_deployment.deployment)
            if user_deployments:
                kuser_id  = user_deployments[0].kuser_id
                driver = self.driver.admin_driver(deployment=site_deployment.deployment.name)
                driver.add_user_role(kuser_id,
                                     site_deployment.tenant_id,
                                     site_priv.role.role)
