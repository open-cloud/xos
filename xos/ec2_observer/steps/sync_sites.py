import os
import base64
from django.db.models import F, Q
from xos.config import Config
from ec2_observer.syncstep import SyncStep
from core.models.site import *
from ec2_observer.awslib import *
import pdb

class SyncSites(SyncStep):
    provides=[Site]
    requested_interval=3600

    def fetch_pending(self, deletion):
        if (deletion):
            return []

        deployment = Deployment.objects.filter(Q(name="Amazon EC2"))[0]
        current_site_deployments = SiteDeployment.objects.filter(Q(deployment=deployment))

        zone_ret = aws_run('ec2 describe-availability-zones')
        zones = zone_ret['AvailabilityZones']

        available_sites = [zone['ZoneName'] for zone in zones]
        site_names = [sd.site.name for sd in current_site_deployments]

        new_site_names = list(set(available_sites) - set(site_names))

        new_sites = []
        for s in new_site_names:
            site = Site(name=s,
                        login_base=s,
                        site_url="www.amazon.com",
                        enabled=True,
                        is_public=True,
                        abbreviated_name=s)
            new_sites.append(site)
        
        return new_sites

    def sync_record(self, site):
        site.save()

