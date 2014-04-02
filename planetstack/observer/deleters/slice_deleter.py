from core.models import Slice, SliceDeployments, User
from observer.deleter import Deleter

class SliceDeleter(Deleter):
	model='Slice'

	def call(self, pk):
		slice = Slice.objects.get(pk=pk)
        slice_deployments = SliceDeployments.objects.filter(slice=slice)
        for slice_deployment in slice_deployments:
            user = User.get(user=slice.creator)
            driver = self.driver.admin_driver(deployment=slice_deployment.deployment.name)
            client_driver = self.driver.client_driver(caller=user,
                                                      tenant=slice.name,
                                                      deployment=slice_deployment.deployment.name) 

            client_driver.delete_router_interface(slice.router_id, slice.subnet_id)
            client_driver.delete_subnet(slice.subnet_id)
            client_driver.delete_router(slice.router_id)
            client_driver.delete_network(slice.network_id)
            driver.delete_tenant(slice.tenant_id)
            # delete external route
            subnet = None
            subnets = client_driver.shell.quantum.list_subnets()['subnets']
            for snet in subnets:
                if snet['id'] == slice.subnet_id:
                    subnet = snet
            if subnet:
                driver.delete_external_route(subnet)
            slice_deployment.delete()
        slice.delete()
