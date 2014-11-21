import os
import base64
from collections import defaultdict
from netaddr import IPAddress, IPNetwork
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.site import Deployment, SiteDeployments
from core.models.slice import Slice, SliceDeployments
from core.models.userdeployments import UserDeployments
from util.logger import Logger, logging
from observer.ansible import *

logger = Logger(level=logging.INFO)

class SyncSliceDeployments(OpenStackSyncStep):
    provides=[SliceDeployments]
    requested_interval=0

    def fetch_pending(self, deleted):
        if (deleted):
            return SliceDeployments.deleted_objects.all()
        else:
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

        if not slice_deployment.deployment.admin_user:
            logger.info("deployment %r has no admin_user, skipping" % slice_deployment.deployment)
            return

	deployment_users = UserDeployments.objects.filter(user=slice_deployment.slice.creator,
                                                             deployment=slice_deployment.deployment)            
    	if not deployment_users:
	    logger.info("slice createor %s has not accout at deployment %s" % (slice_deployment.slice.creator, slice_deployment.deployment.name))
	    roles = []
    	else:
	    deployment_user = deployment_users[0]
	    roles = ['admin']
	    
	max_instances=int(slice_deployment.slice.max_slivers)
	tenant_fields = {'endpoint':slice_deployment.deployment.auth_url,
		         'admin_user': slice_deployment.deployment.admin_user,
		         'admin_password': slice_deployment.deployment.admin_password,
		         'admin_tenant': 'admin',
		         'tenant': slice_deployment.slice.name,
		         'tenant_description': slice_deployment.slice.description,
			 'roles':roles,
			 'name':deployment_user.user.email,
			 'max_instances':max_instances}

	res = run_template('sync_slice_deployments.yaml', tenant_fields)
	expected_num = len(roles)+1
	if (len(res)!=expected_num):
	    raise Exception('Could not sync tenants for slice %s'%slice_deployment.slice.name)
	else:
	    tenant_id = res[0]['id']
	    if (not slice_deployment.tenant_id):
	        handle = os.popen('nova quota-update --instances %d %s'%(max_instances,tenant_id))
		output = handle.read()
		result = handle.close()
		if (result):
		    logging.info('Could not update quota for %s'%slice_deployment.slice.name)
		slice_deployment.tenant_id = tenant_id
		slice_deployment.save()
			


    def delete_record(self, slice_deployment):
        user = User.objects.get(id=slice_deployment.slice.creator.id)
        driver = OpenStackDriver().admin_driver(deployment=slice_deployment.deployment.name)
        client_driver = driver.client_driver(caller=user,
                                             tenant=slice_deployment.slice.name,
                                             deployment=slice_deployment.deployment.name)

        if slice_deployment.router_id and slice_deployment.subnet_id:
            client_driver.delete_router_interface(slice_deployment.router_id, slice_deployment.subnet_id)
        if slice_deployment.subnet_id:
            client_driver.delete_subnet(slice_deployment.subnet_id)
        if slice_deployment.router_id:    
            client_driver.delete_router(slice_deployment.router_id)
        if slice_deployment.network_id:
            client_driver.delete_network(slice_deployment.network_id)
        if slice_deployment.tenant_id:
            driver.delete_tenant(slice_deployment.tenant_id)
        
