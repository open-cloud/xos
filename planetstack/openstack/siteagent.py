import os
import sys
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "planetstack.settings")
import time
from core.models.site import Site
from openstack.manager import OpenStackManager    

class SiteAgent:
    def run(self):
        manager = OpenStackManager()
        # exit if openstack is disable or unavailable
        if manager.enabled and manager.has_openstack:
            # fill in null tenant ids 
            sites = Site.objects.filter(tenant_id__in=[None, ''])
            for site in sites:
                # calling save() on the model should force the tenant_id to be set
                site.os_manager = manager
                site.save() 
                                        
if __name__ == '__main__':
    SiteAgent().run()
                 
