import os
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.slice import *

class SyncSliceMemberships(OpenStackSyncStep):
    requested_interval=0
    provides=[SlicePrivilege]

    def fetch_pending(self):
        return SlicePrivilege.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))

    def sync_record(self, user):
        if slice_memb.user.kuser_id and slice_memb.slice.tenant_id:
                self.driver.add_user_role(slice_memb.user.kuser_id,
                                          slice_memb.slice.tenant_id,
                                          slice_memb.role.role_type)
