import os
import base64
from django.db.models import F, Q
from xos.config import Config
from ec2_observer.syncstep import SyncStep
from core.models.site import *

class SyncDeployments(SyncStep):
    requested_interval=86400
    provides=[Deployment]

    def fetch_pending(self,deletion):
        if (deletion):
            return []

        deployments = Deployment.objects.filter(Q(name="Amazon EC2"))
        if (not deployments):
            deployments = [Deployment(name="Amazon EC2")]
        else:
            deployments = []

        return deployments

    def sync_record(self, deployment):
        deployment.save()
