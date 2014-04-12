from core.models import Site, SiteDeployments
from observer.deleter import Deleter

class SiteDeploymentDeleter(Deleter):
    model='SiteDeployments'

    def call(self, pk):
        site_deployment = SiteDeployments.objects.get(pk=pk)
        if site_deployment.tenant_id:
            driver = self.driver.admin_driver(deployment=site_deployment.deployment.name)
            driver.delete_tenant(site_deployment.tenant_id)
        site_deployment.delete()
