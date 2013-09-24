import os
import base64
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.slice import *

class SyncSliceMemberships(OpenStackSyncStep):
    requested_interval=0
    provides=[SliceRole]
    def sync_record(self, user):
        if slice_memb.user.kuser_id and slice_memb.slice.tenant_id:
                self.driver.add_user_role(slice_memb.user.kuser_id,
                                          slice_memb.slice.tenant_id,
                                          slice_memb.role.role_type)
