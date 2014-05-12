import os
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.slice import *
from core.models.user import UserDeployments
from util.logger import Logger, logging

logger = Logger(level=logging.INFO)

class SyncSliceMemberships(OpenStackSyncStep):
    requested_interval=0
    provides=[SlicePrivilege]

    def fetch_pending(self):
        return SlicePrivilege.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))

    def sync_record(self, slice_memb):
        # sync slice memberships at all slice deployments 
        logger.info("syncing slice privilege: %s %s" % (slice_memb.slice.name, slice_memb.user.email))
        slice_deployments = SliceDeployments.objects.filter(slice=slice_memb.slice)
        for slice_deployment in slice_deployments:
            if not slice_deployment.tenant_id:
                continue
            user_deployments = UserDeployments.objects.filter(deployment=slice_deployment.deployment,
                                                              user=slice_memb.user)
            if user_deployments:
                kuser_id  = user_deployments[0].kuser_id
                driver = self.driver.admin_driver(deployment=slice_deployment.deployment.name)
                driver.add_user_role(kuser_id,
                                     slice_deployment.tenant_id,
                                     slice_memb.role.role)
