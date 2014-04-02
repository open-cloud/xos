from core.models import Site, SiteDeployments
from observer.deleter import Deleter

class SiteDeleter(Deleter):
    model='Site'
    
    def call(self, pk):
        site = Site.objects.get(pk=pk)
        site_deployments = SiteDeployments.objects.filter(site=site)
        for site_deployment in site_deployments:
            if site_deployment.tenant_id:
                driver = self.driver.admin_driver(deployment=site_deployment.deployment.name 
                driver.delete_tenant(site_deployment.tenant_id)
            site_deployment.delete()
        site.delete() 
