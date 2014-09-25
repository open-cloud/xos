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

        name = user_deployment.user.email[:user_deployment.user.email.find('@')]
        user_fields = {'name': user_deployment.user.email,
                       'email': user_deployment.user.email,
                       'password': hashlib.md5(user_deployment.user.password).hexdigest()[:6],
                       'enabled': True}    
        driver = self.driver.admin_driver(deployment=user_deployment.deployment.name)
        if not user_deployment.kuser_id:
            keystone_user = driver.create_user(**user_fields)
            user_deployment.kuser_id = keystone_user.id
        else:
            driver.update_user(user_deployment.kuser_id, user_fields)

        # setup user deployment home site roles  
        if user_deployment.user.site:
            site_deployments = SiteDeployments.objects.filter(site=user_deployment.user.site,
                                                              deployment=user_deployment.deployment)
            if site_deployments:
                # need the correct tenant id for site at the deployment
                tenant_id = site_deployments[0].tenant_id  
                driver.add_user_role(user_deployment.kuser_id, 
                                     tenant_id, 'user')
                if user_deployment.user.is_admin:
                    driver.add_user_role(user_deployment.kuser_id, tenant_id, 'admin')
                else:
                    # may have admin role so attempt to remove it
                    driver.delete_user_role(user_deployment.kuser_id, tenant_id, 'admin')

        #if user_deployment.user.public_key:
        #    if not user_deployment.user.keyname:
        #        keyname = user_deployment.user.email.lower().replace('@', 'AT').replace('.', '')
        #        user_deployment.user.keyname = keyname
        #        user_deployment.user.save()
        #    
        #    user_driver = driver.client_driver(caller=user_deployment.user, 
        #                                       tenant=user_deployment.user.site.login_base, 
        #                                       deployment=user_deployment.deployment.name)
        #    key_fields =  {'name': user_deployment.user.keyname,
        #                   'public_key': user_deployment.user.public_key}
        #    user_driver.create_keypair(**key_fields)

        user_deployment.save()

    def delete_record(self, user_deployment):
        if user_deployment.kuser_id:
            driver = self.driver.admin_driver(deployment=user_deployment.deployment.name)
            driver.delete_user(user_deployment.kuser_id)

