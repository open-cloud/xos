import os
import base64
from django.db.models import F, Q
from xos.config import Config
from openstack_observer.openstacksyncstep import OpenStackSyncStep
from core.models.site import *
from observer.ansible import *

class SyncControllerSites(OpenStackSyncStep):
    requested_interval=0
    provides=[Site]
    observes=ControllerSite

    def fetch_pending(self, deleted=False):
        pending = super(OpenStackSyncStep, self).fetch_pending(deleted)
        return pending.filter(controller__isnull=False)

    def sync_record(self, controller_site):
	template = os_template_env.get_template('sync_controller_sites.yaml')
	tenant_fields = {'endpoint':controller_site.controller.auth_url,
		         'admin_user': controller_site.controller.admin_user,
		         'admin_password': controller_site.controller.admin_password,
		         'admin_tenant': controller_site.controller.admin_tenant,
	                 'ansible_tag': '%s@%s'%(controller_site.site.login_base,controller_site.controller.name), # name of ansible playbook
		         'tenant': controller_site.site.login_base,
		         'tenant_description': controller_site.site.name}

	rendered = template.render(tenant_fields)
	res = run_template('sync_controller_sites.yaml', tenant_fields, path='controller_sites', expected_num=1)

	controller_site.tenant_id = res[0]['id']
	controller_site.backend_status = '1 - OK'
        controller_site.save()
            
    def delete_record(self, controller_site):
	if controller_site.tenant_id:
            driver = self.driver.admin_driver(controller=controller_site.controller)
            driver.delete_tenant(controller_site.tenant_id)

	"""
        Ansible does not support tenant deletion yet

	import pdb
	pdb.set_trace()
        template = os_template_env.get_template('delete_controller_sites.yaml')
	tenant_fields = {'endpoint':controller_site.controller.auth_url,
		         'admin_user': controller_site.controller.admin_user,
		         'admin_password': controller_site.controller.admin_password,
		         'admin_tenant': 'admin',
	                 'ansible_tag': 'controller_sites/%s@%s'%(controller_site.controller_site.site.login_base,controller_site.controller_site.deployment.name), # name of ansible playbook
		         'tenant': controller_site.controller_site.site.login_base,
		         'delete': True}

	rendered = template.render(tenant_fields)
	res = run_template('sync_controller_sites.yaml', tenant_fields)

	if (len(res)!=1):
		raise Exception('Could not assign roles for user %s'%tenant_fields['tenant'])
	"""
