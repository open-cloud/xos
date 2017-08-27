
# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
import base64
from synchronizers.new_base.syncstep import *
from synchronizers.new_base.ansible_helper import *
import json
from mock_modelaccessor import *

class SyncControllerSites(SyncStep):
    requested_interval=0
    provides=[Site]
    observes=ControllerSite
    playbook = 'sync_controller_sites.yaml'

    def fetch_pending(self, deleted=False):
        lobjs = super(SyncControllerSites, self).fetch_pending(deleted)

        if not deleted:
            # filter out objects with null controllers
            lobjs = [x for x in lobjs if x.controller]

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
