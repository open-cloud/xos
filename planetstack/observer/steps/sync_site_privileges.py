import os
import base64
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.site import *

class SyncSitePrivileges(OpenStackSyncStep):
    requested_interval=0
    provides=[SitePrivilege]

    def fetch_pending(self):
        return Network.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))

    def sync_record(self, user):
        if site_priv.user.kuser_id and site_priv.site.tenant_id:
            self.driver.add_user_role(site_priv.user.kuser_id,
                                      site_priv.site.tenant_id,
                                      site_priv.role.role_type) 
