import os
import base64
from collections import defaultdict
from netaddr import IPAddress, IPNetwork
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.deployment import Deployment
from core.models.site import SiteDeployments
from core.models.slice import Slice, SliceDeployments
from core.models.user import UserDeployments
from util.logger import Logger, logging

logger = Logger(level=logging.INFO)

class SyncSliceDeployments(OpenStackSyncStep):
    provides=[SliceDeployments]
    requested_interval=0

    def fetch_pending(self):
        # slice deployments are not visible to users. We must ensure
        # slices are deployed at all deploymets available to their site.
        site_deployments = SiteDeployments.objects.all()
        site_deploy_lookup = defaultdict(list)
        for site_deployment in site_deployments:
            site_deploy_lookup[site_deployment.site].append(site_deployment.deployment)
        
        slice_deployments = SliceDeployments.objects.all()
        slice_deploy_lookup = defaultdict(list)
        for slice_deployment in slice_deployments:
            slice_deploy_lookup[slice_deployment.slice].append(slice_deployment.deployment)
        
        all_deployments = Deployment.objects.all() 
        for slice in Slice.objects.all():
            # slices are added to all deployments for now
            expected_deployments = all_deployments
            #expected_deployments = site_deploy_lookup[slice.site]
            for expected_deployment in expected_deployments:
                if slice not in slice_deploy_lookup or \
                   expected_deployment not in slice_deploy_lookup[slice]:
                    sd = SliceDeployments(slice=slice, deployment=expected_deployment)
                    sd.save()

        # now we can return all slice deployments that need to be enacted   
        return SliceDeployments.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))

    def get_next_subnet(self, deployment=None):
        # limit ourself to 10.0.x.x for now
        valid_subnet = lambda net: net.startswith('10.0')
        driver = self.driver.admin_driver(deployment=deployment)
        subnets = driver.shell.quantum.list_subnets()['subnets']
        ints = [int(IPNetwork(subnet['cidr']).ip) for subnet in subnets \
                if valid_subnet(subnet['cidr'])]
        ints.sort()
        if ints:
            last_ip = IPAddress(ints[-1])
        else:
            last_ip = IPAddress('10.0.0.1')
        last_ip = IPAddress(ints[-1])
        last_network = IPNetwork(str(last_ip) + "/24")
        next_network = IPNetwork(str(IPAddress(last_network) + last_network.size) + "/24")
        return next_network


    def sync_record(self, slice_deployment):
        logger.info("sync'ing slice deployment %s" % slice_deployment)
        if not slice_deployment.tenant_id:
            nova_fields = {'tenant_name': slice_deployment.slice.name,
                   'description': slice_deployment.slice.description,
                   'enabled': slice_deployment.slice.enabled}
            driver = self.driver.admin_driver(deployment=slice_deployment.deployment.name)
            tenant = driver.create_tenant(**nova_fields)
            slice_deployment.tenant_id = tenant.id

            # XXX give caller an admin role at the tenant they've created
            deployment_users = UserDeployments.objects.filter(user=slice_deployment.slice.creator,
                                                             deployment=slice_deployment.deployment)            
            if not deployment_users:
                logger.info("slice createor %s has not accout at deployment %s" % (slice_deployment.slice.creator, slice_deployment.deployment.name))
            else:
                deployment_user = deployment_users[0]
                # lookup user id at this deployment
                kuser= driver.shell.keystone.users.find(email=slice_deployment.slice.creator.email)

                # add required roles at the slice's tenant 
                driver.add_user_role(kuser.id, tenant.id, 'admin')
                    
                # refresh credentials using this tenant
                client_driver = self.driver.client_driver(caller=deployment_user.user,
                                                          tenant=tenant.name, 
                                                          deployment=slice_deployment.deployment.name)


        if slice_deployment.id and slice_deployment.tenant_id:
            # update existing tenant
            driver = self.driver.admin_driver(deployment=slice_deployment.deployment.name)
            driver.update_tenant(slice_deployment.tenant_id,
                                 description=slice_deployment.slice.description,
                                 enabled=slice_deployment.slice.enabled)  

        if slice_deployment.tenant_id:
            # update slice/tenant quota
            driver = self.driver.client_driver(deployment=slice_deployment.deployment.name, tenant=slice_deployment.slice.name)
            driver.shell.nova.quotas.update(tenant_id=slice_deployment.tenant_id, instances=int(slice_deployment.slice.max_slivers)) 

        slice_deployment.save()
