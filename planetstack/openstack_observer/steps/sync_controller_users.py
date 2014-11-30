import os
import base64
import hashlib
from collections import defaultdict
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.site import ControllerSites, Controller
from core.models.user import User
from core.models.usercontrollers import ControllerUsers
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
	
        name = controller_user.user.email[:controller_user.user.email.find('@')]

	roles = []
	# setup user controller home site roles  
        if controller_user.user.site:
            site_controllers = ControllerSites.objects.filter(site=controller_user.user.site,
                                                              controller=controller_user.controller)
            if site_controllers:
                # need the correct tenant id for site at the controller
                tenant_id = site_controllers[0].tenant_id  
		tenant_name = site_controllers[0].site.login_base

		roles.append('user')
                if controller_user.user.is_admin:
                    roles.append('admin')
	    else:
		raise Exception('Internal error. Missing ControllerSites for user %s'%controller_user.user.email)
	else:
	    raise Exception('Siteless user %s'%controller_user.user.email)


        user_fields = {'endpoint':controller_user.controller.auth_url,
		       'name': controller_user.user.email,
                       'email': controller_user.user.email,
                       'password': hashlib.md5(controller_user.user.password).hexdigest()[:6],
                       'admin_user': controller_user.controller.admin_user,
		       'admin_password': controller_user.controller.admin_password,
		       'admin_tenant': 'admin',
		       'roles':roles,
		       'tenant':tenant_name}    
	
	rendered = template.render(user_fields)
	res = run_template('sync_controller_users.yaml', user_fields)

	# results is an array in which each element corresponds to an 
	# "ok" string received per operation. If we get as many oks as
	# the number of operations we issued, that means a grand success.
	# Otherwise, the number of oks tell us which operation failed.
	expected_length = len(roles) + 1
	if (len(res)==expected_length):
        	controller_user.save()
	elif (len(res)):
		raise Exception('Could not assign roles for user %s'%user_fields['name'])
	else:
		raise Exception('Could not create or update user %s'%user_fields['name'])

    def delete_record(self, controller_user):
        if controller_user.kuser_id:
            driver = self.driver.admin_driver(controller=controller_user.controller)
            driver.delete_user(controller_user.kuser_id)
