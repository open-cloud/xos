from core.models import Slice, SliceDeployments, User
from synchronizers.base.deleter import Deleter
from openstack.driver import OpenStackDriver

class SliceDeploymentsDeleter(Deleter):
    model='SliceDeployments'

    def call(self, pk):
        slice_deployment = SliceDeployments.objects.get(pk=pk)
        user = User.objects.get(id=slice_deployment.slice.creator.id)
        driver = OpenStackDriver().admin_driver(deployment=slice_deployment.deployment.name)
        client_driver = driver.client_driver(caller=user,
                                             tenant=slice_deployment.slice.name,
                                             deployment=slice_deployment.deployment.name)

        if slice_deployment.router_id and slice_deployment.subnet_id:
            client_driver.delete_router_interface(slice_deployment.router_id, slice_deployment.subnet_id)
        if slice_deployment.subnet_id:
            client_driver.delete_subnet(slice_deployment.subnet_id)
        if slice_deployment.router_id:    
            client_driver.delete_router(slice_deployment.router_id)
        if slice_deployment.network_id:
            client_driver.delete_network(slice_deployment.network_id)
        if slice_deployment.tenant_id:
            driver.delete_tenant(slice_deployment.tenant_id)
        # delete external route
        #subnet = None
        #subnets = client_driver.shell.quantum.list_subnets()['subnets']
        #for snet in subnets:
        #    if snet['id'] == slice_deployment.subnet_id:
        #        subnet = snet
        #if subnet:
        #    driver.delete_external_route(subnet)
        slice_deployment.delete()
