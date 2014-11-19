from core.models import Site, SiteDeployments
from observer.deleter import Deleter
from observer.deleters.site_deployment_deleter import SiteDeploymentsDeleter

class SiteDeleter(Deleter):
    model='Site'
    
    def call(self, pk):
        site = Site.objects.get(pk=pk)
        site_deployments = SiteDeployments.objects.filter(site=site)
        site_deployment_deleter = SiteDeploymentsDeleter()
        for site_deployment in site_deployments:
            site_deployment_deleter(site_deployment.id)
        site.delete() 
