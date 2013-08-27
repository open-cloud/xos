import os
import base64
from planetstack.config import Config

class SyncSliceMemberships(OpenStackSyncStep):
	provides=[SliceMembership]
	def sync_record(self, user):
		if slice_memb.user.kuser_id and slice_memb.slice.tenant_id:
				self.driver.add_user_role(slice_memb.user.kuser_id,
										  slice_memb.slice.tenant_id,
										  slice_memb.role.role_type)	
	   
