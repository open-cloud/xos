import os
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models import User, UserDeployments, SitePrivilege, SiteDeployments   

class SyncSitePrivileges(OpenStackSyncStep):
    requested_interval=0
    provides=[SitePrivilege]

    def fetch_pending(self):
        return SitePrivilege.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))

    def sync_record(self, site_priv):
        if site_priv.user.kuser_id and site_priv.site.tenant_id:
            self.driver.add_user_role(site_priv.user.kuser_id,
                                      site_priv.site.tenant_id,
                                      site_priv.role.role) 

        # sync site privileges at all site deployments
        site_deployments = SiteDeployments.objects.filter(site=site_priv.site)
        for site_deployment in site_deployments:
            user_deployments = UserDeployments.objects.filter(deployment=site_deployment.deployment)
            if user_deployments:
                kuser_id  = user_deployments[0].kuser_id
                driver = self.driver.admin_driver(deployment=site_deployment.deployment.name)
                driver.add_user_role(kuser_id,
                                     site_deployment.tenant_id,
                                     site_priv.role.role)
