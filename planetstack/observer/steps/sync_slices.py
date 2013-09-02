import os
import base64
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.slice import Slice

class SyncSlices(OpenStackSyncStep):
	provides=[Slice]
	requested_interval=0
	def sync_record(self, slice):
		if not slice.tenant_id:
			nova_fields = {'tenant_name': slice.name,
				   'description': slice.description,
				   'enabled': slice.enabled}
			tenant = self.driver.create_tenant(**nova_fields)
			slice.tenant_id = tenant.id

			# XXX give caller an admin role at the tenant they've created
			self.driver.add_user_role(self.caller.kuser_id, tenant.id, 'admin')

			# refresh credentials using this tenant
			self.driver.shell.connect(username=self.driver.shell.keystone.username,
									  password=self.driver.shell.keystone.password,
									  tenant=tenant.name)

			# create network
			network = self.driver.create_network(slice.name)
			slice.network_id = network['id']

			# create router
			router = self.driver.create_router(slice.name)
			slice.router_id = router['id']

			# create subnet
			next_subnet = self.get_next_subnet()
			cidr = str(next_subnet.cidr)
			ip_version = next_subnet.version
			start = str(next_subnet[2])
			end = str(next_subnet[-2]) 
			subnet = self.driver.create_subnet(name=slice.name,
											   network_id = network['id'],
											   cidr_ip = cidr,
											   ip_version = ip_version,
											   start = start,
											   end = end)
			slice.subnet_id = subnet['id']
			# add subnet as interface to slice's router
			self.driver.add_router_interface(router['id'], subnet['id'])
			# add external route
			self.driver.add_external_route(subnet)


		if slice.id and slice.tenant_id:
			self.driver.update_tenant(slice.tenant_id,
									  description=slice.description,
									  enabled=slice.enabled)   

		slice.save()
