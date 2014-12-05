import os
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models import User, ControllerUsers, SitePrivilege, ControllerSiteDeployments   

class SyncSitePrivileges(OpenStackSyncStep):
    requested_interval=0
    provides=[SitePrivilege]

    def fetch_pending(self, deleted):
        # Deleting site privileges is not supported yet
        if (deleted):
            return []

        return SitePrivilege.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))

    def sync_record(self, site_priv):
        # sync site privileges at all site controllers
        ctrl_site_deployments = ControllerSiteDeployments.objects.filter(site_deployment__site=site_priv.site)
        for ctrl_site_deployment in ctrl_site_deployments:
            controller_users = ControllerUsers.objects.filter(controller=ctrl_site_deployment.controller,
                                                              user=site_priv.user)
            if controller_users:
                kuser_id  = controller_users[0].kuser_id
                driver = self.driver.admin_driver(controller=ctrl_site_deployment.controller)
                driver.add_user_role(kuser_id,
                                     ctrl_site_deployment.controller.tenant_id,
                                     site_priv.role.role)
