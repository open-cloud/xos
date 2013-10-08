import os
import base64
from netaddr import IPAddress, IPNetwork
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.slice import Slice

class SyncSlices(OpenStackSyncStep):
    provides=[Slice]
    requested_interval=0

    def fetch_pending(self):
        return Slice.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))

    def get_next_subnet(self):
        # limit ourself to 10.0.x.x for now
        valid_subnet = lambda net: net.startswith('10.0')
        subnets = self.driver.shell.quantum.list_subnets()['subnets']
        ints = [int(IPNetwork(subnet['cidr']).ip) for subnet in subnets \
                if valid_subnet(subnet['cidr'])]
        ints.sort()
        last_ip = IPAddress(ints[-1])
        last_network = IPNetwork(str(last_ip) + "/24")
        next_network = IPNetwork(str(IPAddress(last_network) + last_network.size) + "/24")

    def sync_record(self, slice):
        if not slice.tenant_id:
            nova_fields = {'tenant_name': slice.name,
                   'description': slice.description,
                   'enabled': slice.enabled}
            tenant = self.driver.create_tenant(**nova_fields)
            slice.tenant_id = tenant.id

            # XXX give caller an admin role at the tenant they've created
            self.driver.add_user_role(slice.creator.kuser_id, tenant.id, 'admin')

            # refresh credentials using this tenant
            client_driver = self.driver.client_driver(tenant=tenant.name)

            # create network
            network = client_driver.create_network(slice.name)
            slice.network_id = network['id']

            # create router
            router = client_driver.create_router(slice.name)
            slice.router_id = router['id']

            # create subnet
            next_subnet = self.get_next_subnet()
            cidr = str(next_subnet.cidr)
            ip_version = next_subnet.version
            start = str(next_subnet[2])
            end = str(next_subnet[-2]) 
            subnet = client_driver.create_subnet(name=slice.name,
                                               network_id = network['id'],
                                               cidr_ip = cidr,
                                               ip_version = ip_version,
                                               start = start,
                                               end = end)
            slice.subnet_id = subnet['id']
            # add subnet as interface to slice's router
            client_driver.add_router_interface(router['id'], subnet['id'])
            # add external route
            client_driver.add_external_route(subnet)


        if slice.id and slice.tenant_id:
            client_driver.update_tenant(slice.tenant_id,
                                      description=slice.description,
                                      enabled=slice.enabled)   

        slice.save()
