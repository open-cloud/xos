import os
import base64
from collections import defaultdict
from django.db.models import F, Q
from xos.config import Config
from synchronizers.base.openstacksyncstep import OpenStackSyncStep
from synchronizers.base.syncstep import *
from core.models.slice import Controller, SlicePrivilege 
from core.models.user import User
from core.models.controlleruser import ControllerUser, ControllerSlicePrivilege
from synchronizers.base.ansible import *
from xos.logger import observer_logger as logger
import json

class SyncControllerSlicePrivileges(OpenStackSyncStep):
    provides=[SlicePrivilege]
    requested_interval=0
    observes=ControllerSlicePrivilege
    playbook = 'sync_controller_users.yaml'

    def map_inputs(self, controller_slice_privilege):
        if not controller_slice_privilege.controller.admin_user:
            logger.info("controller %r has no admin_user, skipping" % controller_slice_privilege.controller)
            return

	template = os_template_env.get_template('sync_controller_users.yaml')
        roles = [controller_slice_privilege.slice_privilege.role.role]
	# setup user home slice roles at controller 
        if not controller_slice_privilege.slice_privilege.user.site:
            raise Exception('Sliceless user %s'%controller_slice_privilege.slice_privilege.user.email)
        else:
            # look up tenant id for the user's slice at the controller
            #ctrl_slice_deployments = SliceDeployment.objects.filter(
            #  slice_deployment__slice=controller_slice_privilege.user.slice,
            #  controller=controller_slice_privilege.controller)

            #if ctrl_slice_deployments:
            #    # need the correct tenant id for slice at the controller
            #    tenant_id = ctrl_slice_deployments[0].tenant_id  
            #    tenant_name = ctrl_slice_deployments[0].slice_deployment.slice.login_base
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
            user = ControllerUser.objects.get(
                controller=controller_slice_privilege.controller, 
                user=controller_slice_privilege.slice_privilege.user
            )
            slice = ControllerSlice.objects.get(
                controller=controller_slice_privilege.controller, 
                user=controller_slice_privilege.slice_privilege.user
            )
            driver.delete_user_role(
                user.kuser_id, 
                slice.tenant_id, 
                controller_slice_privilege.slice_prvilege.role.role
            )
