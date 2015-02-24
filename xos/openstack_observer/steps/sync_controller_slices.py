import os
import base64
from collections import defaultdict
from netaddr import IPAddress, IPNetwork
from django.db.models import F, Q
from xos.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models import User
from core.models.slice import Slice, ControllerSlice
from core.models.controlleruser import ControllerUser
from util.logger import Logger, logging, logger
from observer.ansible import *
from openstack.driver import OpenStackDriver

logger = Logger(level=logging.INFO)

class SyncControllerSlices(OpenStackSyncStep):
    provides=[Slice]
    requested_interval=0
    observes=ControllerSlice

    def fetch_pending(self, deleted):
        if (deleted):
            return ControllerSlice.deleted_objects.all()
        else:
            return ControllerSlice.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))

    def sync_record(self, controller_slice):
        logger.info("sync'ing slice controller %s" % controller_slice)

        if not controller_slice.controller.admin_user:
            logger.info("controller %r has no admin_user, skipping" % controller_slice.controller)
            return

        controller_users = ControllerUser.objects.filter(user=controller_slice.slice.creator,
                                                             controller=controller_slice.controller)
        if not controller_users:
            raise Exception("slice createor %s has not accout at controller %s" % (controller_slice.slice.creator, controller_slice.controller.name))
        else:
            controller_user = controller_users[0]
            roles = ['Admin']

        max_instances=int(controller_slice.slice.max_slivers)
        tenant_fields = {'endpoint':controller_slice.controller.auth_url,
                         'admin_user': controller_slice.controller.admin_user,
                         'admin_password': controller_slice.controller.admin_password,
                         'admin_tenant': 'admin',
                         'tenant': controller_slice.slice.name,
                         'tenant_description': controller_slice.slice.description,
                         'roles':roles,
                         'name':controller_user.user.email,
                         'ansible_tag':'%s@%s'%(controller_slice.slice.name,controller_slice.controller.name),
                         'max_instances':max_instances}

        expected_num = len(roles)+1
        res = run_template('sync_controller_slices.yaml', tenant_fields, path='controller_slices', expected_num=expected_num)
        tenant_id = res[0]['id']
        if (not controller_slice.tenant_id):
            try:
                    driver = OpenStackDriver().admin_driver(controller=controller_slice.controller)
                    driver.shell.nova.quotas.update(tenant_id=controller_slice.tenant_id, instances=int(controller_slice.slice.max_slivers))
            except:
                    logger.log_exc('Could not update quota for %s'%controller_slice.slice.name)
                    raise Exception('Could not update quota for %s'%controller_slice.slice.name)
                
            controller_slice.tenant_id = tenant_id
            controller_slice.backend_status = '1 - OK'
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
