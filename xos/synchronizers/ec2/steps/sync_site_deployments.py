import os
import base64
from django.db.models import F, Q
from xos.config import Config
from ec2_observer.syncstep import SyncStep
from core.models.site import *
from ec2_observer.awslib import *
import pdb

class SyncSiteDeployment(SyncStep):
    requested_interval=86400
    provides=[SiteDeployment]

    def fetch_pending(self, deletion):
        if (deletion):
            return []

        zone_ret = aws_run('ec2 describe-availability-zones')
        zones = zone_ret['AvailabilityZones']
        available_sites = [zone['ZoneName'] for zone in zones]

        current_sites = []
        for s in available_sites:
            site = Site.objects.filter(Q(name=s))
            if (site):
                current_sites.append(site[0])

        # OK not to catch exception
        # The syncstep should catch it
        # At any rate, we should not run if there are no deployments
        deployment = Deployment.objects.filter(Q(name="Amazon EC2"))[0]
        current_site_deployments = SiteDeployment.objects.filter(Q(deployment=deployment))
        site_dict = {}

        for sd in current_site_deployments:
            site_dict[sd.site]=sd

        updated_site_deployments = []
        for site in current_sites:
            try:
                site_record = site_dict[site]
            except KeyError:
                sd = SiteDeployment(site=site,deployment=deployment,tenant_id=base64.urlsafe_b64encode(os.urandom(12)))
                updated_site_deployments.append(sd)

        return updated_site_deployments


    def sync_record(self, site_deployment):
        site_deployment.save()
