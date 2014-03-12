from core.models import Site
from observer.deleter import Deleter

class SiteDeleter(Deleter):
    model='Site'
    
    def call(self, pk):
        site = Site.objects.get(pk=pk)
        if site.tenant_id:
            self.driver.delete_tenant(site.tenant_id)
        site.delete() 
