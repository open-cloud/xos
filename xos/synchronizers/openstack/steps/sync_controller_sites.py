import os
import base64
from django.db.models import F, Q
from xos.config import Config
from synchronizers.openstack.openstacksyncstep import OpenStackSyncStep
from core.models.site import *
from synchronizers.base.syncstep import *
from synchronizers.base.ansible import *
from xos.logger import observer_logger as logger
import json

class SyncControllerSites(OpenStackSyncStep):
    requested_interval=0
    provides=[Site]
    observes=ControllerSite
    playbook = 'sync_controller_sites.yaml'

    def fetch_pending(self, deleted=False):
        lobjs = ControllerSite.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None),Q(lazy_blocked=False),Q(controller__isnull=False))
        return lobjs

    def map_sync_inputs(self, controller_site):
	tenant_fields = {'endpoint':controller_site.controller.auth_url,
                 'endpoint_v3': controller_site.controller.auth_url_v3,
                 'domain': controller_site.controller.domain,
		         'admin_user': controller_site.controller.admin_user,
		         'admin_password': controller_site.controller.admin_password,
		         'admin_tenant': controller_site.controller.admin_tenant,
	             'ansible_tag': '%s@%s'%(controller_site.site.login_base,controller_site.controller.name), # name of ansible playbook
		         'tenant': controller_site.site.login_base,
		         'tenant_description': controller_site.site.name}
        return tenant_fields

    def map_sync_outputs(self, controller_site, res):
	controller_site.tenant_id = res[0]['id']
	controller_site.backend_status = '1 - OK'
        controller_site.save()
            
    def delete_record(self, controller_site):
	controller_register = json.loads(controller_site.controller.backend_register)
        if (controller_register.get('disabled',False)):
                raise InnocuousException('Controller %s is disabled'%controller_site.controller.name)

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
