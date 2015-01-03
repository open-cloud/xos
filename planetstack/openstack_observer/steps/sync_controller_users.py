import os
import base64
from collections import defaultdict
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.site import Controller, SiteDeployments, ControllerSiteDeployments
from core.models.user import User
from core.models.controllerusers import ControllerUsers
from util.logger import Logger, logging

from observer.ansible import *

logger = Logger(level=logging.INFO)

class SyncControllerUsers(OpenStackSyncStep):
    provides=[ControllerUsers, User]
    requested_interval=0

    def fetch_pending(self, deleted):

        if (deleted):
            return ControllerUsers.deleted_objects.all()
        else:
            return ControllerUsers.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None)) 

    def sync_record(self, controller_user):
        logger.info("sync'ing user %s at controller %s" % (controller_user.user, controller_user.controller))

        if not controller_user.controller.admin_user:
            logger.info("controller %r has no admin_user, skipping" % controller_user.controller)
            return

	template = os_template_env.get_template('sync_controller_users.yaml')

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
            #ctrl_site_deployments = ControllerSiteDeployments.objects.filter(
            #  site_deployment__site=controller_user.user.site,
            #  controller=controller_user.controller)

            #if ctrl_site_deployments:
            #    # need the correct tenant id for site at the controller
            #    tenant_id = ctrl_site_deployments[0].tenant_id  
            #    tenant_name = ctrl_site_deployments[0].site_deployment.site.login_base
            user_fields = {
                       'endpoint':controller_user.controller.auth_url,
		       'name': controller_user.user.email,
                       'email': controller_user.user.email,
                       'password': controller_user.user.remote_password,
                       'admin_user': controller_user.controller.admin_user,
		       'admin_password': controller_user.controller.admin_password,
	               'ansible_tag':'%s@%s'%(controller_user.user.email.replace('@','-at-'),controller_user.controller.name),
		       'admin_tenant': controller_user.controller.admin_tenant,
		       'roles':roles,
		       'tenant':controller_user.user.site.login_base}    
	
	    rendered = template.render(user_fields)
	    res = run_template('sync_controller_users.yaml', user_fields,path='controller_users')

	    # results is an array in which each element corresponds to an 
	    # "ok" string received per operation. If we get as many oks as
	    # the number of operations we issued, that means a grand success.
	    # Otherwise, the number of oks tell us which operation failed.
	    expected_length = len(roles) + 1
	    if (len(res)==expected_length):
                controller_user.kuser_id = res[0]['id']
                controller_user.save()
	    elif (len(res)):
	        raise Exception('Could not assign roles for user %s'%user_fields['name'])
	    else:
	        raise Exception('Could not create or update user %s'%user_fields['name'])

    def delete_record(self, controller_user):
        if controller_user.kuser_id:
            driver = self.driver.admin_driver(controller=controller_user.controller)
            driver.delete_user(controller_user.kuser_id)
