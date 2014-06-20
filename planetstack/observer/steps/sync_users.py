import os
import base64
import hashlib
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.user import User
from core.models.userdeployments import  UserDeployments

class SyncUsers(OpenStackSyncStep):
    provides=[User]
    requested_interval=0

    def fetch_pending(self):
        return User.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))

    def sync_record(self, user):
        for user_deployment in UserDeployments.objects.filter(user=user):
            # bump the 'updated' field so user account are updated across 
            # deployments.
            user_deployment.save()
