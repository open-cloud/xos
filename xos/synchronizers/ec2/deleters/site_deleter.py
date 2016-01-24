from core.models import Site, SiteDeployment
from synchronizers.base.deleter import Deleter
from synchronizers.base.deleters.site_deployment_deleter import SiteDeploymentDeleter

class SiteDeleter(Deleter):
    model='Site'
    
    def call(self, pk):
        site = Site.objects.get(pk=pk)
        site_deployments = SiteDeployment.objects.filter(site=site)
        site_deployment_deleter = SiteDeploymentDeleter()
        for site_deployment in site_deployments:
            site_deployment_deleter(site_deployment.id)
        site.delete() 
