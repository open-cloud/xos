
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
import json
from synchronizers.new_base.ansible_helper import *
from mock_modelaccessor import *
import syncstep

class SyncControllerSlicePrivileges(syncstep.SyncStep):
    provides=[SlicePrivilege]
    requested_interval=0
    observes=ControllerSlicePrivilege
    playbook = 'sync_controller_users.yaml'

    def map_sync_inputs(self, controller_slice_privilege):
        if not controller_slice_privilege.controller.admin_user:
            return

	template = os_template_env.get_template('sync_controller_users.yaml')
        roles = [controller_slice_privilege.slice_privilege.role.role]
	# setup user home slice roles at controller 
        if not controller_slice_privilege.slice_privilege.user.site:
            raise Exception('Sliceless user %s'%controller_slice_privilege.slice_privilege.user.email)
        else:
            user_fields = {
               'endpoint':controller_slice_privilege.controller.auth_url,
               'endpoint_v3': controller_slice_privilege.controller.auth_url_v3,
               'domain': controller_slice_privilege.controller.domain,
		       'name': controller_slice_privilege.slice_privilege.user.email,
               'email': controller_slice_privilege.slice_privilege.user.email,
               'password': controller_slice_privilege.slice_privilege.user.remote_password,
               'admin_user': controller_slice_privilege.controller.admin_user,
		       'admin_password': controller_slice_privilege.controller.admin_password,
               'ansible_tag':'%s@%s@%s'%(controller_slice_privilege.slice_privilege.user.email.replace('@','-at-'),controller_slice_privilege.slice_privilege.slice.name,controller_slice_privilege.controller.name),
		       'admin_tenant': controller_slice_privilege.controller.admin_tenant,
		       'roles':roles,
		       'tenant':controller_slice_privilege.slice_privilege.slice.name}    
            return user_fields
	
    def map_sync_outputs(self, controller_slice_privilege, res):
        controller_slice_privilege.role_id = res[0]['id']
        controller_slice_privilege.save()

    def delete_record(self, controller_slice_privilege):
	controller_register = json.loads(controller_slice_privilege.controller.backend_register)
        if (controller_register.get('disabled',False)):
                raise InnocuousException('Controller %s is disabled'%controller_slice_privilege.controller.name)

        if controller_slice_privilege.role_id:
            driver = self.driver.admin_driver(controller=controller_slice_privilege.controller)
            user = ControllerUser.objects.filter(
                controller_id=controller_slice_privilege.controller.id,
                user_id=controller_slice_privilege.slice_privilege.user.id
            )
            user = user[0]
            slice = ControllerSlice.objects.filter(
                controller_id=controller_slice_privilege.controller.id,
                user_id=controller_slice_privilege.slice_privilege.user.id
            )
            slice = slice[0]
            driver.delete_user_role(
                user.kuser_id, 
                slice.tenant_id, 
                controller_slice_privilege.slice_prvilege.role.role
            )
