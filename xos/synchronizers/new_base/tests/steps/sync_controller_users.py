
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
from mock_modelaccessor import *

class SyncControllerUsers(SyncStep):
    provides=[User]
    requested_interval=0
    observes=ControllerUser
    playbook='sync_controller_users.yaml'

    def map_sync_inputs(self, controller_user):
        if not controller_user.controller.admin_user:
            return

        # All users will have at least the 'user' role at their home site/tenant.
        # We must also check if the user should have the admin role

        roles = ['user']
        if controller_user.user.is_admin:
            driver = self.driver.admin_driver(controller=controller_user.controller)
            roles.append(driver.get_admin_role().name)

        # setup user home site roles at controller
        if not controller_user.user.site:
            raise Exception('Siteless user %s'%controller_user.user.email)
        else:
            user_fields = {
                'endpoint':controller_user.controller.auth_url,
                'endpoint_v3': controller_user.controller.auth_url_v3,
                'domain': controller_user.controller.domain,
                'name': controller_user.user.email,
                'email': controller_user.user.email,
                'password': controller_user.user.remote_password,
                'admin_user': controller_user.controller.admin_user,
                'admin_password': controller_user.controller.admin_password,
                'ansible_tag':'%s@%s'%(controller_user.user.email.replace('@','-at-'),controller_user.controller.name),
                'admin_project': controller_user.controller.admin_tenant,
                'roles':roles,
                'project':controller_user.user.site.login_base
                }
	    return user_fields

    def map_sync_outputs(self, controller_user, res):
        controller_user.kuser_id = res[0]['user']['id']
        controller_user.backend_status = '1 - OK'
        controller_user.save()

    def delete_record(self, controller_user):
        if controller_user.kuser_id:
            driver = self.driver.admin_driver(controller=controller_user.controller)
            driver.delete_user(controller_user.kuser_id)
