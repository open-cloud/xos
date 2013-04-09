from plstackapi.planetstack.config import Config
from plstackapi.openstack.client import OpenStackClient

class OpenStackDriver:

    def __init__(self, config = None, client=None): 
        if config:
            self.config = Config(config)
        else:
            self.config = Config() 

        if client:
            self.shell = client
        else:
            self.shell = OpenStackClient()

    def create_role(self, name): 
        roles = self.shell.keystone.roles.findall(name=name)
        if not roles:
            role = self.shell.keystone.roles.create(name)
        else:
            role = roles[0] 
        return role

    def delete_role(self, filter):
        roles = self.shell.keystone.roles.findall(**filter)
        for role in roles:
            self.shell.keystone.roles.delete(role)
        return 1

    def create_tenant(self, tenant_name, enabled, description):
        """Create keystone tenant. Suggested fields: name, description, enabled"""  
        tenants = self.shell.keystone.tenants.findall(name=tenant_name)
        if not tenants:
            fields = {'tenant_name': tenant_name, 'enabled': enabled, 
                      'description': description}  
            tenant = self.shell.keystone.tenants.create(**fields)
        else:
            tenant = tenants[0]
        return tenant

    def update_tenant(self, id, **kwds):
        return self.shell.keystone.tenants.update(id, **kwds)

    def delete_tenant(self, id):
        tenant = self.shell.keystone.tenants.find(id=id)
        return self.shell.keystone.tenants.delete(tenant)

    def create_user(self, name, email, password, enabled):
        users = self.shell.keystone.users.findall(email=email)
        if not users:
            fields = {'name': name, 'email': email, 'password': password,
                      'enabled': enabled}
            user = self.shell.keystone.users.create(**fields)
        else: 
            user = users[0]
        return user

    def add_user_role(self, user_id, tenant_id, role_name):
        user = self.shell.keystone.users.find(id=user_id)
        tenant = self.shell.keystone.tenants.find(id=tenant_id)
        role = self.shell.keystone.roles.find(role_name)
        return tenant.add_user(user, role)

    def delete_user_role(self, user_id, tenant_id, role_name):
        user = self.shell.keystone.users.find(id=user_id)
        tenant = self.shell.keystone.tenants.find(id=tenant_id)
        role = self.shell.keystone.roles.find(role_name)
        return tenant.delete_user(user, role)

    def update_user(self, id, **kwds):
        return self.shell.keystone.users.update(id, **kwds)

    def delete_user(self, id):
        user = self.shell.keystone.users.find(id=id)
        return self.shell.keystone.users.delete(user)  

    def create_router(self, name, set_gateway=True):
        router = self.shell.quantum.create_router(name=name)
        if set_gateway:
            nets = self.shell.quantum.list_networks()
            for net in nets:
                if net['router:external'] == True: 
                    self.shell.quantum.add_gateway_router(router, net)
        
        return router

    def delete_router(self, name):
        return self.shell.quantum.delete_router(name=name)

    def add_router_interface(self, router_id, subnet_id):
        router = None
        subnet = None
        for r in self.shell.quantum.list_routers():
            if r['id'] == router_id:
                router = r
                break
        for s in self.shell.quantum.list_subnets():
            if s['id'] == subnet_id:
                subnet = s
                break

        if router and subnet:
            self.shell.quantum.router_add_interface(router, subnet)

    def delete_router_interface(self, router_id, subnet_id):
        router = None
        subnet = None
        for r in self.shell.quantum.list_routers():
            if r['id'] == router_id:
                router = r
                break
        for s in self.shell.quantum.list_subnets():
            if s['id'] == subnet_id:
                subnet = s
                break

        if router and subnet:
            self.shell.quantum.router_remove_interface(router, subnet)            
 
    def create_network(self, name):
        return self.shell.quantum.create_network(name=name, admin_state_up=True)
    
    def delete_network(self, name):
        nets = self.shell.quantum.list_networks(name=name)
        for net in nets:
            # delete all subnets:
            #subnets = self.api.client_shell.quantum.list_subnets(network_id=net['network_id'])['subnets']
            for subnet_id in net['subnets']:
                self.delete_subnet(subnet_id)
            self.shell.quantum.delete_network(net['id'])
    
    def create_subnet(self, network_name, cidr_ip, ip_version, start, end):
        nets = self.shell.quantum.list_networks(name=network_name)
        if not nets:
            raise Exception, "No such network: %s" % network_name   
        nets = nets[0]

        subnets = self.shell.quantum.list_subnets(name=self.name)
        allocation_pools = [{'start': start, 'end': end}]
        subnet = self.shell.quantum.create_subnet(network_id=net['id'],
                                                ip_version=ip_version,
                                                cidr=cidr_ip,
                                                dns_nameservers=['8.8.8.8', '8.8.8.4'],         
                                                allocation_pools=allocation_pools)

        # TODO: Add route to external network
        # e.g. #  route add -net 10.0.3.0/24 dev br-ex gw 10.100.0.5 
        return subnet

    def delete_subnet(self, id):
        return self.client.quantum.delete_subnet(id=id)
     
    
    def create_keypair(self, name, key):
        keys = self.client.nova.keypairs.findall(name=name)
        if keys:
            raise Exception, "Key name already exists: %s" % name
        return self.client.nova.keypairs.create(name=name, public_key=key)

    def delete_keypair(self, name):
        keys = self.client.nova.keypairs.findall(name=name)
        for key in keys:
            self.client.nova.keypairs.delete(key) 

    def spawn_instance(self, name, key_name=None, hostname=None, flavor=None, image=None, security_group=None, pubkeys=[]):
        if not flavor:
            flavor = self.config.nova_default_flavor
        if not image:
            image = self.config.nova_default_imave
        if not security_group:
            security_group = self.config.nova_default_security_group 

        authorized_keys = "\n".join(pubkeys)
        files = {'/root/.ssh/authorized_keys': authorized_keys}
       
        flavor_id = self.shell.nova.flavors.find(name=flavor)
        images = self.shell.glance.get_images(name=image)
        if not images:
            raise Exception, "Image not found: " + image  
        image_id = images[0]['id']
        hints = {}
        if hostname:
            hints['force_hosts']= hostname
        server = self.shell.nova.servers.create(
                                            name=name,
                                            key_name = key_name,
                                            flavor=flavor_id,
                                            image=image_id,
                                            security_group = security_group,
                                            files=files,
                                            scheduler_hints=hints)
        return server
          
    def destroy_instance(self, name, id=None):
        args = {'name': name}
        if id:
            args['id'] = id
        servers = self.shell.nova.servers.findall(**args)
        for server in servers:
            if name == server.name:
                if not id or id == server.id:
                    self.shell.nova.servers.delete(server)
