import os
import base64
from collections import defaultdict
from django.db.models import F, Q
from xos.config import Config
from synchronizers.base.openstacksyncstep import OpenStackSyncStep
from synchronizers.base.syncstep import *
from core.models.site import Controller, SiteDeployment, SiteDeployment
from core.models.user import User
from core.models.controlleruser import ControllerUser
from synchronizers.base.ansible import *
from xos.logger import observer_logger as logger
import json

class SyncControllerUsers(OpenStackSyncStep):
    provides=[User]
    requested_interval=0
    observes=ControllerUser
    playbook='sync_controller_users.yaml'

    def map_sync_inputs(self, controller_user):
        if not controller_user.controller.admin_user:
            logger.info("controller %r has no admin_user, skipping" % controller_user.controller)
            return

        # All users will have at least the 'user' role at their home site/tenant.
        # We must also check if the user should have the admin role
        roles = ['user']
        if controller_user.user.is_admin:
            roles.append('admin')

        # setup user home site roles at controller
        if not controller_user.user.site:
            raise Exception('Siteless user %s'%controller_user.user.email)
        else:
            # look up tenant id for the user's site at the controller
            #ctrl_site_deployments = SiteDeployment.objects.filter(
            #  site_deployment__site=controller_user.user.site,
            #  controller=controller_user.controller)

            #if ctrl_site_deployments:
            #    # need the correct tenant id for site at the controller
            #    tenant_id = ctrl_site_deployments[0].tenant_id
            #    tenant_name = ctrl_site_deployments[0].site_deployment.site.login_base
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
                'admin_tenant': controller_user.controller.admin_tenant,
                'roles':roles,
                'tenant':controller_user.user.site.login_base
                }
	    return user_fields

    def map_sync_outputs(self, controller_user, res):
        controller_user.kuser_id = res[0]['id']
        controller_user.backend_status = '1 - OK'
        controller_user.save()

    def delete_record(self, controller_user):
        if controller_user.kuser_id:
            driver = self.driver.admin_driver(controller=controller_user.controller)
            driver.delete_user(controller_user.kuser_id)
