import os
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.syncstep import SyncStep
from core.models.site import Site
from ec2_observer.awslib import *

class SyncSites(SyncStep):
    provides=[Site]
    requested_interval=3600

    def fetch_pending(self):
		current_sites = Site.objects.all()
		zones = aws_run('ec2 describe-availability-zones')
		available_sites = [zone['ZoneName'] for zone in zones]

		new_site_names = list(set(available_sites) - set(zones))

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

