import os
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.role import Role
from core.models.site import SiteRole
from core.models.slice import SliceRole
from core.models.deployment import DeploymentRole

class SyncRoles(OpenStackSyncStep):
    provides=[Role]
    requested_interval=0

    def fetch_pending(self):
        site_roles = SiteRole.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))
        slice_roles = SliceRole.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))
        deployment_roles = DeploymentRole.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))

        roles = []
        for site_role in site_roles:
            roles.append(site_role)
        for slice_role in slice_roles:
            roles.append(slice_role)
        for deployment_role in deployment_roles:
            roles.append(deployment_role)

        return roles


    def sync_record(self, role):
        if not role.enacted:
            deployments = Deployment.objects.all()
            for deployment in deployments:
                driver = self.driver.admin_driver(deployment=deployment.name)
                driver.create_role(role.role)
            role.save()    
