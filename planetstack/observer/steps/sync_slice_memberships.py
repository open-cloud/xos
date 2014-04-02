import os
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.slice import *
from core.models.user import UserDeployments

class SyncSliceMemberships(OpenStackSyncStep):
    requested_interval=0
    provides=[SlicePrivilege]

    def fetch_pending(self):
        return SlicePrivilege.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))

    def sync_record(self, slice_memb):
        if slice_memb.user.kuser_id and slice_memb.slice.tenant_id:
                self.driver.add_user_role(slice_memb.user.kuser_id,
                                          slice_memb.slice.tenant_id,
                                          slice_memb.role.role)

        # sync slice memberships at all slice deployments 
        slice_deployments = SliceDeployments.objects.filter(slice=slice_memb.slice)
        for slice_deployment in slice_deployments:
            user_deployments = UserDeployments.objects.filter(deployment=slice_deployment.deployment)
            if user_deployments:
                kuser_id  = user_deployments[0].kuser_id
                driver = self.driver.admin_driver(deployment=slice_deployment.deployment.name)
                driver.add_user_role(kuser_id,
                                     slice_deployment.tenant_id,
                                     slice_memb.role.role)
