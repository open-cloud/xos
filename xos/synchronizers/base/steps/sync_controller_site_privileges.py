import os
import base64
from collections import defaultdict
from django.db.models import F, Q
from xos.config import Config
from synchronizers.base.openstacksyncstep import OpenStackSyncStep
from synchronizers.base.syncstep import *
from core.models.site import Controller, SitePrivilege 
from core.models.user import User
from core.models.controlleruser import ControllerUser, ControllerSitePrivilege
from xos.logger import observer_logger as logger
from synchronizers.base.ansible import *
import json

class SyncControllerSitePrivileges(OpenStackSyncStep):
    provides=[SitePrivilege]
    requested_interval=0
    observes=ControllerSitePrivilege
    playbook='sync_controller_users.yaml'

    def map_sync_inputs(self, controller_site_privilege):
	controller_register = json.loads(controller_site_privilege.controller.backend_register)
        if not controller_site_privilege.controller.admin_user:
            logger.info("controller %r has no admin_user, skipping" % controller_site_privilege.controller)
            return

        roles = [controller_site_privilege.site_privilege.role.role]
	# setup user home site roles at controller 
        if not controller_site_privilege.site_privilege.user.site:
            raise Exception('Siteless user %s'%controller_site_privilege.site_privilege.user.email)
        else:
            # look up tenant id for the user's site at the controller
            #ctrl_site_deployments = SiteDeployment.objects.filter(
            #  site_deployment__site=controller_site_privilege.user.site,
            #  controller=controller_site_privilege.controller)

            #if ctrl_site_deployments:
            #    # need the correct tenant id for site at the controller
            #    tenant_id = ctrl_site_deployments[0].tenant_id  
            #    tenant_name = ctrl_site_deployments[0].site_deployment.site.login_base
            user_fields = {
               'endpoint':controller_site_privilege.controller.auth_url,
               'endpoint_v3': controller_site_privilege.controller.auth_url_v3,
               'domain': controller_site_privilege.controller.domain,
		       'name': controller_site_privilege.site_privilege.user.email,
               'email': controller_site_privilege.site_privilege.user.email,
               'password': controller_site_privilege.site_privilege.user.remote_password,
               'admin_user': controller_site_privilege.controller.admin_user,
		       'admin_password': controller_site_privilege.controller.admin_password,
	           'ansible_tag':'%s@%s'%(controller_site_privilege.site_privilege.user.email.replace('@','-at-'),controller_site_privilege.controller.name),
		       'admin_tenant': controller_site_privilege.controller.admin_tenant,
		       'roles':roles,
		       'tenant':controller_site_privilege.site_privilege.site.login_base}    
	
	    return user_fields

    def map_sync_outputs(self, controller_site_privilege, res):
	    # results is an array in which each element corresponds to an 
	    # "ok" string received per operation. If we get as many oks as
	    # the number of operations we issued, that means a grand success.
	    # Otherwise, the number of oks tell us which operation failed.
            controller_site_privilege.role_id = res[0]['id']
            controller_site_privilege.save()

    def delete_record(self, controller_site_privilege):
	controller_register = json.loads(controller_site_privilege.controller.backend_register)
        if (controller_register.get('disabled',False)):
                raise InnocuousException('Controller %s is disabled'%controller_site_privilege.controller.name)

        if controller_site_privilege.role_id:
            driver = self.driver.admin_driver(controller=controller_site_privilege.controller)
            user = ControllerUser.objects.get(
                controller=controller_site_privilege.controller, 
                user=controller_site_privilege.site_privilege.user
            )
            site = ControllerSite.objects.get(
                controller=controller_site_privilege.controller, 
                user=controller_site_privilege.site_privilege.user
            )
            driver.delete_user_role(
                user.kuser_id, 
                site.tenant_id, 
                controller_site_privilege.site_prvilege.role.role
            )
