import os
import base64
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.user import User

class SyncUsers(OpenStackSyncStep):
	provides=[User]
	requested_interval=0
	def sync_record(self, user):
		name = user.email[:user.email.find('@')]
		user_fields = {'name': name,
					   'email': user.email,
					   'password': hashlib.md5(user.password).hexdigest()[:6],
					   'enabled': True}
		if not user.kuser_id:
			keystone_user = self.driver.create_user(**user_fields)
			user.kuser_id = keystone_user.id
		else:
			self.driver.update_user(user.kuser_id, user_fields)		

		if user.site:
			self.driver.add_user_role(user.kuser_id, user.site.tenant_id, 'user')
			if user.is_admin:
				self.driver.add_user_role(user.kuser_id, user.site.tenant_id, 'admin')
			else:
				# may have admin role so attempt to remove it
				self.driver.delete_user_role(user.kuser_id, user.site.tenant_id, 'admin')

		if user.public_key:
			self.init_caller(user, user.site.login_base)
			self.save_key(user.public_key, user.keyname)
			self.init_admin()

		user.save()
