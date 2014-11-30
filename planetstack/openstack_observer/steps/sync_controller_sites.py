import os
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.site import *
from observer.ansible import *

class SyncControllerSites(OpenStackSyncStep):
    requested_interval=0
    provides=[Controller, Site]

    def sync_record(self, controller):

	template = os_template_env.get_template('sync_controller_sites.yaml')
	tenant_fields = {'endpoint':controller.auth_url,
		         'admin_user': controller.admin_user,
		         'admin_password': controller.admin_password,
		         'admin_tenant': 'admin',
		         'tenant': controller.site_deployment.site.login_base,
		         'tenant_description': controller.site_deployment.site.name}

	rendered = template.render(tenant_fields)
	res = run_template('sync_controller_sites.yaml', tenant_fields)

	if (len(res)==1):
		controller.tenant_id = res[0]['id']
        	controller.save()
	elif (len(res)):
		raise Exception('Could not assign roles for user %s'%tenant_fields['tenant'])
	else:
		raise Exception('Could not create or update user %s'%tenant_fields['tenant'])
            
    def delete_record(self, controller):
        if controller.tenant_id:
            driver = self.driver.admin_driver(controller=controller)
            driver.delete_tenant(controller.tenant_id)
