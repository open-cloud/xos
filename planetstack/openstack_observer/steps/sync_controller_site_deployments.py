import os
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.site import *
from observer.ansible import *

class SyncControllerSiteDeployments(OpenStackSyncStep):
    requested_interval=0
    provides=[ControllerSiteDeployments, SiteDeployments]

    def sync_record(self, controller_site_deployment):

	template = os_template_env.get_template('sync_controller_site_deployments.yaml')
	tenant_fields = {'endpoint':controller_site_deployment.controller.auth_url,
		         'admin_user': controller_site_deployment.controller.admin_user,
		         'admin_password': controller_site_deployment.controller.admin_password,
		         'admin_tenant': 'admin',
		         'tenant': controller_site_deployment.site_deployment.site.login_base,
		         'tenant_description': controller_site_deployment.site_deployment.site.name}

	rendered = template.render(tenant_fields)
	res = run_template('sync_controller_site_deployments.yaml', tenant_fields)

	if (len(res)==1):
		controller_site_deployment.tenant_id = res[0]['id']
        	controller_site_deployment.save()
	elif (len(res)):
		raise Exception('Could not assign roles for user %s'%tenant_fields['tenant'])
	else:
		raise Exception('Could not create or update user %s'%tenant_fields['tenant'])
            
    def delete_record(self, controller_site_deployment):
        if controller_site_deployment.tenant_id:
            driver = self.driver.admin_driver(controller=controller_site_deployment.controller)
            driver.delete_tenant(controller_site_deployment.tenant_id)
