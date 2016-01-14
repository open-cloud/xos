import os
import base64
import datetime
from django.db.models import F, Q
from xos.config import Config
from synchronizers.base.openstacksyncstep import OpenStackSyncStep
from core.models.user import User
from xos.logger import observer_logger as logger

class SyncRoles(OpenStackSyncStep):
    provides=[User]
    requested_interval=0
    observes=User

    def fetch_pending(self, deleted):
        if (deleted):
            # users marked as deleted
            return User.deleted_objects.all()
        else:
            # disabled users that haven't been updated in over a week 
            one_week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
            return User.objects.filter(is_active=False, updated__gt=one_week_ago)             

    def sync_record(self, user):
        user.delete() 
