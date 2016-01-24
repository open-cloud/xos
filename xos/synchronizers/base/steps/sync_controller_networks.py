import os
import base64
from collections import defaultdict
from netaddr import IPAddress, IPNetwork
from django.db.models import F, Q
from xos.config import Config
from synchronizers.base.openstacksyncstep import OpenStackSyncStep
from synchronizers.base.syncstep import *
from core.models.network import *
from core.models.slice import *
from core.models.instance import Instance
from xos.logger import observer_logger as logger
from synchronizers.base.ansible import *
from openstack.driver import OpenStackDriver
from xos.config import Config
import json

import pdb

class SyncControllerNetworks(OpenStackSyncStep):
    requested_interval = 0
    provides=[Network]
    observes=ControllerNetwork	
    playbook='sync_controller_networks.yaml'

    def alloc_subnet(self, uuid):
        # 16 bits only
        uuid_masked = uuid & 0xffff
        a = 10
        b = uuid_masked >> 8
        c = uuid_masked & 0xff
        d = 0

        cidr = '%d.%d.%d.%d/24'%(a,b,c,d)
        return cidr

    def alloc_gateway(self, uuid):
        # 16 bits only
        uuid_masked = uuid & 0xffff
        a = 10
        b = uuid_masked >> 8
        c = uuid_masked & 0xff
        d = 1

        gateway = '%d.%d.%d.%d'%(a,b,c,d)
        return gateway


    def save_controller_network(self, controller_network):
        network_name = controller_network.network.name
        subnet_name = '%s-%d'%(network_name,controller_network.pk)
        cidr = self.alloc_subnet(controller_network.pk)
        self.cidr=cidr
        slice = controller_network.network.owner

        network_fields = {'endpoint':controller_network.controller.auth_url,
                    'endpoint_v3': controller_network.controller.auth_url_v3,
                    'admin_user':slice.creator.email,
                    'tenant_name':slice.name,
                    'admin_password':slice.creator.remote_password,
                    'domain': controller_network.controller.domain,
                    'name':network_name,
                    'subnet_name':subnet_name,
                    'ansible_tag':'%s-%s@%s'%(network_name,slice.slicename,controller_network.controller.name),
                    'cidr':cidr,
                    'gateway':self.alloc_gateway(controller_network.pk),
                    'use_vtn':getattr(Config(), "networking_use_vtn", False),
                    'delete':False	
                    }
        return network_fields

    def map_sync_outputs(self, controller_network,res):
        network_id = res[0]['id']
        subnet_id = res[1]['id']
        controller_network.net_id = network_id
        controller_network.subnet = self.cidr
        controller_network.subnet_id = subnet_id
	controller_network.backend_status = '1 - OK'
        controller_network.save()


    def map_sync_inputs(self, controller_network):
        # XXX This check should really be made from booleans, rather than using hardcoded network names
        if (controller_network.network.template.name not in ['Private', 'Private-Indirect', 'Private-Direct']):
            logger.info("skipping network controller %s because it is not private" % controller_network)
            # We only sync private networks
            return SyncStep.SYNC_WITHOUT_RUNNING
        
        if not controller_network.controller.admin_user:
            logger.info("controller %r has no admin_user, skipping" % controller_network.controller)
            return

        if controller_network.network.owner and controller_network.network.owner.creator:
	    return self.save_controller_network(controller_network)
        else:
            raise Exception('Could not save network controller %s'%controller_network)

    def map_delete_inputs(self, controller_network):
        # XXX This check should really be made from booleans, rather than using hardcoded network names
	if (controller_network.network.template.name not in ['Private', 'Private-Indirect', 'Private-Direct']):
            # We only sync private networks
            return
	try:
        	slice = controller_network.network.owner # XXX: FIXME!!
        except:
                raise Exception('Could not get slice for Network %s'%controller_network.network.name)

	network_name = controller_network.network.name
        subnet_name = '%s-%d'%(network_name,controller_network.pk)
	cidr = controller_network.subnet
	network_fields = {'endpoint':controller_network.controller.auth_url,
                    'admin_user':slice.creator.email, # XXX: FIXME
                    'tenant_name':slice.name, # XXX: FIXME
                    'admin_password':slice.creator.remote_password,
                    'name':network_name,
                    'subnet_name':subnet_name,
                    'ansible_tag':'%s-%s@%s'%(network_name,slice.slicename,controller_network.controller.name),
                    'cidr':cidr,
		    'delete':True	
                    }

        return network_fields

	"""
        driver = OpenStackDriver().client_driver(caller=controller_network.network.owner.creator,
                                                 tenant=controller_network.network.owner.name,
                                                 controller=controller_network.controller.name)
        if (controller_network.router_id) and (controller_network.subnet_id):
            driver.delete_router_interface(controller_network.router_id, controller_network.subnet_id)
        if controller_network.subnet_id:
            driver.delete_subnet(controller_network.subnet_id)
        if controller_network.router_id:
            driver.delete_router(controller_network.router_id)
        if controller_network.net_id:
            driver.delete_network(controller_network.net_id)
	"""
