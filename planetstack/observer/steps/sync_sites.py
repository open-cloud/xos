import os
import base64
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.site import Site

class SyncSites(OpenStackSyncStep):
	provides=[Site]
	requested_interval=0

    def fetch_pending(self):
        return Site.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))

	def sync_record(self, site):
		save_site = False
		if not site.tenant_id:
			tenant = self.driver.create_tenant(tenant_name=site.login_base,
											   description=site.name,
											   enabled=site.enabled)
			site.tenant_id = tenant.id
			save_site = True
			# XXX - What's caller?
			# self.driver.add_user_role(self.caller.kuser_id, tenant.id, 'admin')

		# update the record
		if site.id and site.tenant_id:
			self.driver.update_tenant(site.tenant_id,
									  description=site.name,
									  enabled=site.enabled)

		if (save_site):
			site.save() # 

