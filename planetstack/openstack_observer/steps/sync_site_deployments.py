import os
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.site import *
from observer.ansible import *

class SyncSiteDeployments(OpenStackSyncStep):
    requested_interval=0
    provides=[SiteDeployments, Site]

    def sync_record(self, site_deployment):

	template = os_template_env.get_template('sync_site_deployments.yaml')
	tenant_fields = {'endpoint':site_deployment.deployment.auth_url,
		         'admin_user': site_deployment.deployment.admin_user,
		         'admin_password': site_deployment.deployment.admin_password,
		         'admin_tenant': 'admin',
		         'tenant': site_deployment.site.login_base,
		         'tenant_description': site_deployment.site.name}

	rendered = template.render(tenant_fields)
	res = run_template('sync_site_deployments.yaml', tenant_fields)

	if (len(res)==1):
		site_deployment.tenant_id = res[0]['id']
        	site_deployment.save()
	elif (len(res)):
		raise Exception('Could not assign roles for user %s'%tenant_fields['tenant'])
	else:
		raise Exception('Could not create or update user %s'%tenant_fields['tenant'])
            
    def delete_record(self, site_deployment):
        if site_deployment.tenant_id:
            driver = self.driver.admin_driver(deployment=site_deployment.deployment.name)
            driver.delete_tenant(site_deployment.tenant_id)
