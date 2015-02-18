import os
import base64
from collections import defaultdict
from netaddr import IPAddress, IPNetwork
from django.db.models import F, Q
from xos.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.network import *
from core.models.slice import *
from core.models.sliver import Sliver
from util.logger import Logger, logging
from observer.ansible import *
from openstack.driver import OpenStackDriver

import pdb

logger = Logger(level=logging.INFO)

class SyncControllerNetworks(OpenStackSyncStep):
    requested_interval = 0
    provides=[Network]
    observes=ControllerNetwork	

    def alloc_subnet(self, uuid):
        # 16 bits only
        uuid_masked = uuid & 0xffff
        a = 10
        b = uuid_masked >> 8
        c = uuid_masked & 0xff
        d = 0

        cidr = '%d.%d.%d.%d/24'%(a,b,c,d)
        return cidr


    def fetch_pending(self, deleted):
        if (deleted):
            return ControllerNetwork.deleted_objects.all()
        else:
            return ControllerNetwork.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))


    def save_controller_network(self, controller_network):
        network_name = controller_network.network.name
        subnet_name = '%s-%d'%(network_name,controller_network.pk)
        cidr = self.alloc_subnet(controller_network.pk)
        slice = controller_network.network.slices.all()[0] # XXX: FIXME!!

        network_fields = {'endpoint':controller_network.controller.auth_url,
                    'admin_user':slice.creator.email, # XXX: FIXME
                    'tenant_name':slice.name, # XXX: FIXME
                    'admin_password':slice.creator.remote_password,
                    'name':network_name,
                    'subnet_name':subnet_name,
                    'ansible_tag':'%s-%s@%s'%(network_name,slice.slicename,controller_network.controller.name),
                    'cidr':cidr
                    }

        res = run_template('sync_controller_networks.yaml', network_fields, path = 'controller_networks',expected_num=2)

        network_id = res[0]['id']
        subnet_id = res[1]['id']
        controller_network.net_id = network_id
        controller_network.subnet = cidr
        controller_network.subnet_id = subnet_id
	controller_network.backend_status = '1 - OK'
        controller_network.save()


    def sync_record(self, controller_network):
        logger.info("sync'ing network controller %s for network %s slice %s controller %s" % (controller_network, controller_network.network, str(controller_network.network.owner), controller_network.controller))

        if not controller_network.controller.admin_user:
            logger.info("controller %r has no admin_user, skipping" % controller_network.controller)
            return

        if controller_network.network.owner and controller_network.network.owner.creator:
	    self.save_controller_network(controller_network)
	    logger.info("saved network controller: %s" % (controller_network))

    def delete_record(self, controller_network):
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
