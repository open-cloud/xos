from core.models import Slice
from observer.deleter import Deleter

class SliceDeleter(Deleter):
	model='Slice'

	def call(self, pk):
		slice = Slice.objects.get(pk=pk)
        self.driver.delete_router_interface(slice.router_id, slice.subnet_id)
        self.driver.delete_subnet(slice.subnet_id)
        self.driver.delete_router(slice.router_id)
        self.driver.delete_network(slice.network_id)
        self.driver.delete_tenant(slice.tenant_id)
        # delete external route
        subnet = None
        subnets = self.driver.shell.quantum.list_subnets()['subnets']
        for snet in subnets:
            if snet['id'] == slice.subnet_id:
                subnet = snet
        if subnet:
            self.driver.delete_external_route(subnet)
        slice.delete()
