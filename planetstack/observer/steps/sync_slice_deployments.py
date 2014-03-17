import os
import base64
from collections import defaultdict
from netaddr import IPAddress, IPNetwork
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.site import SiteDeployments
from core.models.slice import Slice, SliceDeployments
from core.models.user import UserDeployments
from util.logger import Logger, logging

logger = Logger(level=logging.INFO)

class SyncSliceDeployments(OpenStackSyncStep):
    provides=[Slice, SliceDeployments]
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
        
        for slice in Slice.objects.all():
            expected_deployments = site_deploy_lookup[slice.site]
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
                # lookup user id at this deployment
                kuser= driver.shell.keystone.users.find(email=slice_deployment.slice.creator.email)
                driver.add_user_role(kuser.id, tenant.id, 'admin')

                # refresh credentials using this tenant
                client_driver = self.driver.client_driver(tenant=tenant.name, 
                                                          deployment=slice_deployment.deployment.name)

                # create network
                network = client_driver.create_network(slice_deployment.slice.name)
                slice_deployment.network_id = network['id']

                # create router
                router = client_driver.create_router(slice_deployment.slice.name)
                slice_deployment.router_id = router['id']

                # create subnet for slice's private network
                next_subnet = self.get_next_subnet(deployment=slice_deployment.deployment.name)
                cidr = str(next_subnet.cidr)
                ip_version = next_subnet.version
                start = str(next_subnet[2])
                end = str(next_subnet[-2]) 
                subnet = client_driver.create_subnet(name=slice_deployment.slice.name,
                                                   network_id = network['id'],
                                                   cidr_ip = cidr,
                                                   ip_version = ip_version,
                                                   start = start,
                                                   end = end)
                slice_deployment.subnet_id = subnet['id']
                # add subnet as interface to slice's router
                client_driver.add_router_interface(router['id'], subnet['id'])
                # add external route
                client_driver.add_external_route(subnet)


        if slice_deployment.id and slice_deployment.tenant_id:
            driver = self.driver.admin_driver(deployment=slice_deployment.deployment.name)
            driver.update_tenant(slice_deployment.tenant_id,
                                 description=slice_deployment.slice.description,
                                 enabled=slice_deployment.slice.enabled)   

        slice_deployment.save()
