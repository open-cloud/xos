import os
import base64
from collections import defaultdict
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.site import SiteDeployments
from core.models.user import User, UserDeployments
from util.logger import Logger, logging

logger = Logger(level=logging.INFO)

class SyncUserDeployments(OpenStackSyncStep):
    provides=[User, UserDeployments]
    requested_interval=0

    def fetch_pending(self):
        # user deployments are not visible to users. We must ensure
        # user are deployed at all deploymets available to their sites.
        site_deployments = SiteDeployment.objects.all()
        site_deploy_lookup = defaultdict(list)
        for site_deployment in site_deployments:
            site_deploy_lookup[site_deployment.site].append(site_deployment.deployment)
        
        user_deployments = UserDeployment.objects.all()
        user_deploy_lookup = defaultdict(list)
        for user_deployment in user_deployments:
            user_deploy_lookup[user_deployment.user].append(user_deployment.deployment)
        
        for user in User.objects.all():
            expected_deployments = site_deploy_lookup[user.site]
            for expected_deployment in expected_deployments:
                if expected_deployment not in user_deploy_lookup[user]:
                    ud = UserDeployments(user=user, deployment=expected_deployment)
                    ud.save()

        # now we can return all slice deployments that need to be enacted   
        return UserDeployments.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))

    def sync_record(self, user_deployment):
        logger.info("sync'ing user deployment %s" % user_deployment.name)
        name = user_deployment.user.email[:user_deployment.user.email.find('@')]
        user_fields = {'name': name,
                       'email': user_deployment.user.email,
                       'password': hashlib.md5(user_deployment.user.password).hexdigest()[:6],
                       'enabled': True}    
        driver = self.driver.admin_driver(deployment=user_deployment.deployment.name)
        if not user_deployment.kuser_id:
            keystone_user = self.driver.create_user(**user_fields)
            user_deployment.kuser_id = keystone_user.id
        else:
            driver.update_user(user_deployment.kuser_id, user_fields)

        # setup user deployment site roles  
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

        if user_deployment.user.public_key:
            user_driver = self.driver.client_driver(caller=user, tenant=user.site.login_base, 
                                                    deployment=user_deployment.deployment.name)
            key_fields =  {'name': user_deployment.user.keyname,
                           'public_key': user_deployment.user.public_key}
            user_driver.create_keypair(**key_fields)

        user_deployment.save()
