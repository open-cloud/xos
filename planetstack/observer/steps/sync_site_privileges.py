import os
import base64
from planetstack.config import Config

class SyncSitePrivileges(OpenStackSyncStep):
	provides=[SitePrivilege]
	def sync_record(self, user):
	   if site_priv.user.kuser_id and site_priv.site.tenant_id:
			self.driver.add_user_role(site_priv.user.kuser_id,
									  site_priv.site.tenant_id,
									  site_priv.role.role_type) 
