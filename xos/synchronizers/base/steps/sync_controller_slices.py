import os
import base64
from collections import defaultdict
from netaddr import IPAddress, IPNetwork
from django.db.models import F, Q
from xos.config import Config
from synchronizers.base.openstacksyncstep import OpenStackSyncStep
from synchronizers.base.syncstep import *
from core.models import *
from synchronizers.base.ansible import *
from openstack.driver import OpenStackDriver
from xos.logger import observer_logger as logger
import json

class SyncControllerSlices(OpenStackSyncStep):
    provides=[Slice]
    requested_interval=0
    observes=ControllerSlice
    playbook='sync_controller_slices.yaml'

    def map_sync_inputs(self, controller_slice):
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
            roles = ['admin']

        max_instances=int(controller_slice.slice.max_instances)
        tenant_fields = {'endpoint':controller_slice.controller.auth_url,
                         'endpoint_v3': controller_slice.controller.auth_url_v3,
                         'domain': controller_slice.controller.domain,
                         'admin_user': controller_slice.controller.admin_user,
                         'admin_password': controller_slice.controller.admin_password,
                         'admin_tenant': 'admin',
                         'tenant': controller_slice.slice.name,
                         'tenant_description': controller_slice.slice.description,
                         'roles':roles,
                         'name':controller_user.user.email,
                         'ansible_tag':'%s@%s'%(controller_slice.slice.name,controller_slice.controller.name),
                         'max_instances':max_instances}

        return tenant_fields

    def map_sync_outputs(self, controller_slice, res):
        tenant_id = res[0]['id']
        if (not controller_slice.tenant_id):
            try:
                driver = OpenStackDriver().admin_driver(controller=controller_slice.controller)
                driver.shell.nova.quotas.update(tenant_id=tenant_id, instances=int(controller_slice.slice.max_instances))
            except:
                logger.log_exc('Could not update quota for %s'%controller_slice.slice.name)
                raise Exception('Could not update quota for %s'%controller_slice.slice.name)

            controller_slice.tenant_id = tenant_id
            controller_slice.backend_status = '1 - OK'
            controller_slice.save()


    def map_delete_inputs(self, controller_slice):
        controller_users = ControllerUser.objects.filter(user=controller_slice.slice.creator,
                                                              controller=controller_slice.controller)
        if not controller_users:
            raise Exception("slice createor %s has not accout at controller %s" % (controller_slice.slice.creator, controller_slice.controller.name))
        else:
            controller_user = controller_users[0]

        tenant_fields = {'endpoint':controller_slice.controller.auth_url,
                          'admin_user': controller_slice.controller.admin_user,
                          'admin_password': controller_slice.controller.admin_password,
                          'admin_tenant': 'admin',
                          'tenant': controller_slice.slice.name,
                          'tenant_description': controller_slice.slice.description,
                          'name':controller_user.user.email,
                          'ansible_tag':'%s@%s'%(controller_slice.slice.name,controller_slice.controller.name),
                          'delete': True}
	return tenant_fields
