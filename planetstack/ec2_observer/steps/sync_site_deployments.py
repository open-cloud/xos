import os
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.site import *

class SyncSiteDeployments(OpenStackSyncStep):
    requested_interval=0
    provides=[Site, SiteDeployments]

    def fetch_pending(self):
        return SiteDeployments.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))

    def sync_record(self, site_deployment):
        if not site_deployment.tenant_id:
            driver = self.driver.admin_driver(deployment=site_deployment.deployment.name)
            tenant = driver.create_tenant(tenant_name=site_deployment.site.login_base,
                                               description=site_deployment.site.name,
                                               enabled=site_deployment.site.enabled)
            site_deployment.tenant_id = tenant.id
            site_deployment.save()
        elif site_deployment.site.id and site_deployment.tenant_id:
            driver = self.driver.admin_driver(deployment=site_deployment.name)
            driver.update_tenant(site_deployment.tenant_id,
                                 description=site_deployment.site.name,
                                 enabled=site_deployment.site.enabled)
            
