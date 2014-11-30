import os
import base64
from collections import defaultdict
from netaddr import IPAddress, IPNetwork
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.site import Controller, ControllerSites
from core.models.slice import Slice, ControllerSlices
from core.models.usercontrollers import ControllerUsers
from util.logger import Logger, logging
from observer.ansible import *

logger = Logger(level=logging.INFO)

class SyncControllerSlices(OpenStackSyncStep):
    provides=[ControllerSlices]
    requested_interval=0

    def fetch_pending(self, deleted):
        if (deleted):
            return ControllerSlices.deleted_objects.all()
        else:
            return ControllerSlices.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))

    def get_next_subnet(self, controller=None):
        # limit ourself to 10.0.x.x for now
        valid_subnet = lambda net: net.startswith('10.0')
        driver = self.driver.admin_driver(controller=controller)
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


    def sync_record(self, controller_slice):
        logger.info("sync'ing slice controller %s" % controller_slice)

        if not controller_slice.controller.admin_user:
            logger.info("controller %r has no admin_user, skipping" % controller_slice.controller)
            return

	controller_users = ControllerUsers.objects.filter(user=controller_slice.slice.creator,
                                                             controller=controller_slice.controller)            
    	if not controller_users:
	    logger.info("slice createor %s has not accout at controller %s" % (controller_slice.slice.creator, controller_slice.controller.name))
	    roles = []
    	else:
	    controller_user = controller_users[0]
	    roles = ['admin']
	    
	max_instances=int(controller_slice.slice.max_slivers)
	tenant_fields = {'endpoint':controller_slice.controller.auth_url,
		         'admin_user': controller_slice.controller.admin_user,
		         'admin_password': controller_slice.controller.admin_password,
		         'admin_tenant': 'admin',
		         'tenant': controller_slice.slice.name,
		         'tenant_description': controller_slice.slice.description,
			 'roles':roles,
			 'name':controller_user.user.email,
			 'max_instances':max_instances}

	res = run_template('sync_controller_slices.yaml', tenant_fields)
	expected_num = len(roles)+1
	if (len(res)!=expected_num):
	    raise Exception('Could not sync tenants for slice %s'%controller_slice.slice.name)
	else:
	    tenant_id = res[0]['id']
	    if (not controller_slice.tenant_id):
	        handle = os.popen('nova quota-update --instances %d %s'%(max_instances,tenant_id))
		output = handle.read()
		result = handle.close()
		if (result):
		    logging.info('Could not update quota for %s'%controller_slice.slice.name)
		controller_slice.tenant_id = tenant_id
		controller_slice.save()
			


    def delete_record(self, controller_slice):
        user = User.objects.get(id=controller_slice.slice.creator.id)
        driver = OpenStackDriver().admin_driver(controller=controller_slice.controller.name)
        client_driver = driver.client_driver(caller=user,
                                             tenant=controller_slice.slice.name,
                                             controller=controller_slice.controller.name)

        if controller_slice.router_id and controller_slice.subnet_id:
            client_driver.delete_router_interface(controller_slice.router_id, controller_slice.subnet_id)
        if controller_slice.subnet_id:
            client_driver.delete_subnet(controller_slice.subnet_id)
        if controller_slice.router_id:    
            client_driver.delete_router(controller_slice.router_id)
        if controller_slice.network_id:
            client_driver.delete_network(controller_slice.network_id)
        if controller_slice.tenant_id:
            driver.delete_tenant(controller_slice.tenant_id)
        
