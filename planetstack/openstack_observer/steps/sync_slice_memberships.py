import os
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.slice import *
from core.models.controllerusers import ControllerUsers
from util.logger import Logger, logging

logger = Logger(level=logging.INFO)

class SyncSliceMemberships(OpenStackSyncStep):
    requested_interval=0
    provides=[SlicePrivilege]

    def fetch_pending(self, deleted):
        # Deleting site memberships is not supported yet
        if (deleted):
            return []
        return SlicePrivilege.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))

    def sync_record(self, slice_memb):
        # sync slice memberships at all slice controllers 
        logger.info("syncing slice privilege: %s %s" % (slice_memb.slice.name, slice_memb.user.email))
        slice_controllers = ControllerSlices.objects.filter(slice=slice_memb.slice)
        for slice_controller in slice_controllers:
            if not slice_controller.tenant_id:
                continue
            controller_users = ControllerUsers.objects.filter(controller=slice_controller.controller,
                                                              user=slice_memb.user)
            if controller_users:
                kuser_id  = controller_users[0].kuser_id
                driver = self.driver.admin_driver(controller=slice_controller.controller.name)
                driver.add_user_role(kuser_id,
                                     slice_controller.tenant_id,
                                     slice_memb.role.role)
