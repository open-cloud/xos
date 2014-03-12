import os
import base64
import hashlib
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.user import User

class SyncUsers(OpenStackSyncStep):
    provides=[User]
    requested_interval=0

    def fetch_pending(self):
        return User.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))

    def sync_record(self, user):
        user.save()
