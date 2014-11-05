import os
import base64
import hashlib
from collections import defaultdict
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.site import SiteDeployments, Deployment
from core.models.user import User
from core.models.userdeployments import UserDeployments
from util.logger import Logger, logging

from observer.ansible import *

logger = Logger(level=logging.INFO)

class SyncUserDeployments(OpenStackSyncStep):
    provides=[UserDeployments, User]
    requested_interval=0

    def fetch_pending(self, deleted):

        if (deleted):
            return UserDeployments.deleted_objects.all()
        else:
            return UserDeployments.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None)) 

    def sync_record(self, user_deployment):
        logger.info("sync'ing user %s at deployment %s" % (user_deployment.user, user_deployment.deployment.name))

        if not user_deployment.deployment.admin_user:
            logger.info("deployment %r has no admin_user, skipping" % user_deployment.deployment)
            return

	template = os_template_env.get_template('sync_user_deployments.yaml')
	
        name = user_deployment.user.email[:user_deployment.user.email.find('@')]

	roles = []
	# setup user deployment home site roles  
        if user_deployment.user.site:
            site_deployments = SiteDeployments.objects.filter(site=user_deployment.user.site,
                                                              deployment=user_deployment.deployment)
            if site_deployments:
                # need the correct tenant id for site at the deployment
                tenant_id = site_deployments[0].tenant_id  
		tenant_name = site_deployments[0].site.login_base

		roles.append('user')
                if user_deployment.user.is_admin:
                    roles.append('admin')
	    else:
		raise Exception('Internal error. Missing SiteDeployment for user %s'%user_deployment.user.email)
	else:
	    raise Exception('Siteless user %s'%user_deployment.user.email)


        user_fields = {'endpoint':user_deployment.deployment.auth_url,
		       'name': user_deployment.user.email,
                       'email': user_deployment.user.email,
                       'password': hashlib.md5(user_deployment.user.password).hexdigest()[:6],
                       'admin_user': user_deployment.deployment.admin_user,
		       'admin_password': user_deployment.deployment.admin_password,
		       'admin_tenant': 'admin',
		       'roles':roles,
		       'tenant':tenant_name}    
	
	rendered = template.render(user_fields)
	res = run_template('sync_user_deployments.yaml', user_fields)

	# results is an array in which each element corresponds to an 
	# "ok" string received per operation. If we get as many oks as
	# the number of operations we issued, that means a grand success.
	# Otherwise, the number of oks tell us which operation failed.
	expected_length = len(roles) + 1
	if (len(res)==expected_length):
        	user_deployment.save()
	elif (len(res)):
		raise Exception('Could not assign roles for user %s'%user_fields['name'])
	else:
		raise Exception('Could not create or update user %s'%user_fields['name'])

    def delete_record(self, user_deployment):
        if user_deployment.kuser_id:
            driver = self.driver.admin_driver(deployment=user_deployment.deployment.name)
            driver.delete_user(user_deployment.kuser_id)
