import commands
import hashlib
from xos.config import Config
from core.models import Controller

try:
    from openstack.client import OpenStackClient
    has_openstack = True
except:
    has_openstack = False

manager_enabled = Config().api_nova_enabled

class OpenStackDriver:

    def __init__(self, config = None, client=None):
        if config:
            self.config = Config(config)
        else:
            self.config = Config()

        if client:
            self.shell = client

        self.enabled = manager_enabled
        self.has_openstack = has_openstack
        self.controller = None
        self.admin_user = None

    def client_driver(self, caller=None, tenant=None, controller=None):
        if caller:
            auth = {'username': caller.email,
                    'password': hashlib.md5(caller.password).hexdigest()[:6],
                    'tenant': tenant}
            client = OpenStackClient(controller=controller, cacert=self.config.nova_ca_ssl_cert, **auth)
        else:
            admin_driver = self.admin_driver(tenant=tenant, controller=controller)
            client = OpenStackClient(tenant=tenant, controller=admin_driver.controller)

        driver = OpenStackDriver(client=client)
        #driver.admin_user = admin_driver.admin_user
        #driver.controller = admin_driver.controller
        return driver

    def admin_driver(self, tenant=None, controller=None):
        if isinstance(controller, int):
            controller = Controller.objects.get(id=controller.id)
        if not tenant:
            tenant = controller.admin_tenant
        client = OpenStackClient(tenant=tenant, controller=controller, cacert=self.config.nova_ca_ssl_cert)
        driver = OpenStackDriver(client=client)
        driver.admin_user = client.keystone.users.find(name=controller.admin_user)
        driver.controller = controller
        return driver    

    def create_role(self, name):
        roles = self.shell.keystone.roles.findall(name=name)
        roles_title = self.shell.keystone.roles.findall(name=name.title())
        roles_found = roles + roles_title
        if not roles_found:
            role = self.shell.keystone.roles.create(name)
        else:
            role = roles_found[0]
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

        # always give the admin user the admin role to any tenant created 
        # by the driver. 
        self.add_user_role(self.admin_user.id, tenant.id, 'admin')
        return tenant

    def update_tenant(self, id, **kwds):
        return self.shell.keystone.tenants.update(id, **kwds)

    def delete_tenant(self, id):
        ctx = self.shell.nova_db.ctx
        tenants = self.shell.keystone.tenants.findall(id=id)
        for tenant in tenants:
            # nova does not automatically delete the tenant's instances
            # so we manually delete instances before deleteing the tenant   
            instances = self.shell.nova_db.instance_get_all_by_filters(ctx,
                       {'project_id': tenant.id}, 'id', 'asc')
            client = OpenStackClient(tenant=tenant.name)
            driver = OpenStackDriver(client=client)
            for instance in instances:
                driver.destroy_instance(instance.id)
            self.shell.keystone.tenants.delete(tenant)
        return 1

    def create_user(self, name, email, password, enabled):
        users = self.shell.keystone.users.findall(email=email)
        if not users:
            fields = {'name': name, 'email': email, 'password': password,
                      'enabled': enabled}
            user = self.shell.keystone.users.create(**fields)
        else: 
            user = users[0]
        return user

    def delete_user(self, id):
        users = self.shell.keystone.users.findall(id=id)
        for user in users:
            # delete users keys
            keys = self.shell.nova.keypairs.findall()
            for key in keys:
                self.shell.nova.keypairs.delete(key)
            self.shell.keystone.users.delete(user)
        return 1

    def get_admin_role(self):
        role = None
        for admin_role_name in ['admin', 'Admin']:
            roles = self.shell.keystone.roles.findall(name=admin_role_name)
            if roles:
                role = roles[0]
                break
        return role 

    def add_user_role(self, kuser_id, tenant_id, role_name):
        user = self.shell.keystone.users.find(id=kuser_id)
        tenant = self.shell.keystone.tenants.find(id=tenant_id)
        # admin role can be lowercase or title. Look for both
        role = None
        if role_name.lower() == 'admin':
            role = self.get_admin_role()
        else:
            # look up non admin role or force exception when admin role isnt found 
            role = self.shell.keystone.roles.find(name=role_name)                   

        role_found = False
        user_roles = user.list_roles(tenant.id)
        for user_role in user_roles:
            if user_role.name == role.name:
                role_found = True
        if not role_found:
            tenant.add_user(user, role)

        return 1

    def delete_user_role(self, kuser_id, tenant_id, role_name):
        user = self.shell.keystone.users.find(id=kuser_id)
        tenant = self.shell.keystone.tenants.find(id=tenant_id)
        # admin role can be lowercase or title. Look for both
        role = None
        if role_name.lower() == 'admin':
            role = self.get_admin_role()
        else:
            # look up non admin role or force exception when admin role isnt found
            role = self.shell.keystone.roles.find(name=role_name)

        role_found = False
        user_roles = user.list_roles(tenant.id)
        for user_role in user_roles:
            if user_role.name == role.name:
                role_found = True
        if role_found:
            tenant.remove_user(user, role)

        return 1 

    def update_user(self, id, fields):
        if 'password' in fields:
            self.shell.keystone.users.update_password(id, fields['password'])
        if 'enabled' in fields:
            self.shell.keystone.users.update_enabled(id, fields['enabled']) 
        return 1 

    def create_router(self, name, set_gateway=True):
        routers = self.shell.quantum.list_routers(name=name)['routers']
        if routers:
            router = routers[0]
        else:
            router = self.shell.quantum.create_router({'router': {'name': name}})['router']
        # add router to external network
        if set_gateway:
            nets = self.shell.quantum.list_networks()['networks']
            for net in nets:
                if net['router:external'] == True: 
                    self.shell.quantum.add_gateway_router(router['id'],
                                                          {'network_id': net['id']})
        
        return router

    def delete_router(self, id):
        routers = self.shell.quantum.list_routers(id=id)['routers']
        for router in routers:
            self.shell.quantum.delete_router(router['id'])
            # remove router form external network
            #nets = self.shell.quantum.list_networks()['networks']
            #for net in nets:
            #    if net['router:external'] == True:
            #        self.shell.quantum.remove_gateway_router(router['id'])

    def add_router_interface(self, router_id, subnet_id):
        router = self.shell.quantum.show_router(router_id)['router']
        subnet = self.shell.quantum.show_subnet(subnet_id)['subnet']
        if router and subnet:
            self.shell.quantum.add_interface_router(router_id, {'subnet_id': subnet_id})

    def delete_router_interface(self, router_id, subnet_id):
        router = self.shell.quantum.show_router(router_id)
        subnet = self.shell.quantum.show_subnet(subnet_id)
        if router and subnet:
            self.shell.quantum.remove_interface_router(router_id, {'subnet_id': subnet_id})
 
    def create_network(self, name, shared=False):
        nets = self.shell.quantum.list_networks(name=name)['networks']
        if nets: 
            net = nets[0]
        else:
            net = self.shell.quantum.create_network({'network': {'name': name, 'shared': shared}})['network']
        return net
 
    def delete_network(self, id):
        nets = self.shell.quantum.list_networks()['networks']
        for net in nets:
            if net['id'] == id:
                # delete_all ports
                self.delete_network_ports(net['id'])
                # delete all subnets:
                for subnet_id in net['subnets']:
                    self.delete_subnet(subnet_id)
                self.shell.quantum.delete_network(net['id'])
        return 1

    def delete_network_ports(self, network_id):
        ports = self.shell.quantum.list_ports()['ports']
        for port in ports:
            if port['network_id'] == network_id:
                self.shell.quantum.delete_port(port['id'])
        return 1         

    def delete_subnet_ports(self, subnet_id):
        ports = self.shell.quantum.list_ports()['ports']
        for port in ports:
            delete = False
            for fixed_ip in port['fixed_ips']:
                if fixed_ip['subnet_id'] == subnet_id:
                    delete=True
                    break
            if delete:
                self.shell.quantum.delete_port(port['id'])
        return 1
 
    def create_subnet(self, name, network_id, cidr_ip, ip_version, start, end):
        #nets = self.shell.quantum.list_networks(name=network_name)['networks']
        #if not nets:
        #    raise Exception, "No such network: %s" % network_name   
        #net = nets[0]

        subnet = None 
        subnets = self.shell.quantum.list_subnets()['subnets']
        for snet in subnets:
            if snet['cidr'] == cidr_ip and snet['network_id'] == network_id:
                subnet = snet

        if not subnet:
            # HACK: Add metadata route -- Neutron does not reliably supply this
            metadata_ip = cidr_ip.replace("0/24", "3")

            allocation_pools = [{'start': start, 'end': end}]
            subnet = {'subnet': {'name': name,
                                 'network_id': network_id,
                                 'ip_version': ip_version,
                                 'cidr': cidr_ip,
                                 #'dns_nameservers': ['8.8.8.8', '8.8.4.4'],
                                 'host_routes': [{'destination':'169.254.169.254/32','nexthop':metadata_ip}],
                                 'gateway_ip': None,
                                 'allocation_pools': allocation_pools}}
            subnet = self.shell.quantum.create_subnet(subnet)['subnet']
            # self.add_external_route(subnet)

        return subnet

    def update_subnet(self, id, fields):
        return self.shell.quantum.update_subnet(id, fields)

    def delete_subnet(self, id):
        #return self.shell.quantum.delete_subnet(id=id)
        # inefficient but fault tolerant
        subnets = self.shell.quantum.list_subnets()['subnets']
        for subnet in subnets:
            if subnet['id'] == id:
                self.delete_subnet_ports(subnet['id'])
                self.shell.quantum.delete_subnet(id)
                self.delete_external_route(subnet)
        return 1

    def get_external_routes(self):
        status, output = commands.getstatusoutput('route')
        routes = output.split('\n')[3:]
        return routes

    def add_external_route(self, subnet, routes=[]):
        if not routes:
            routes = self.get_external_routes()
 
        ports = self.shell.quantum.list_ports()['ports']

        gw_ip = subnet['gateway_ip']
        subnet_id = subnet['id']

        # 1. Find the port associated with the subnet's gateway
        # 2. Find the router associated with that port
        # 3. Find the port associated with this router and on the external net
        # 4. Set up route to the subnet through the port from step 3
        ip_address = None
        for port in ports:
            for fixed_ip in port['fixed_ips']:
                if fixed_ip['subnet_id'] == subnet_id and fixed_ip['ip_address'] == gw_ip:
                    gw_port = port
                    router_id = gw_port['device_id']
                    router = self.shell.quantum.show_router(router_id)['router']
                    if router and router.get('external_gateway_info'):
                        ext_net = router['external_gateway_info']['network_id']
                        for port in ports:
                            if port['device_id'] == router_id and port['network_id'] == ext_net:
                                ip_address = port['fixed_ips'][0]['ip_address']

        if ip_address:
            # check if external route already exists
            route_exists = False
            if routes:
                for route in routes:
                    if subnet['cidr'] in route and ip_address in route:
                        route_exists = True
            if not route_exists:
                cmd = "route add -net %s dev br-ex gw %s" % (subnet['cidr'], ip_address)
                s, o = commands.getstatusoutput(cmd)
                #print cmd, "\n", s, o

        return 1

    def delete_external_route(self, subnet):
        ports = self.shell.quantum.list_ports()['ports']

        gw_ip = subnet['gateway_ip']
        subnet_id = subnet['id']

        # 1. Find the port associated with the subnet's gateway
        # 2. Find the router associated with that port
        # 3. Find the port associated with this router and on the external net
        # 4. Set up route to the subnet through the port from step 3
        ip_address = None
        for port in ports:
            for fixed_ip in port['fixed_ips']:
                if fixed_ip['subnet_id'] == subnet_id and fixed_ip['ip_address'] == gw_ip:
                    gw_port = port
                    router_id = gw_port['device_id']
                    router = self.shell.quantum.show_router(router_id)['router']
                    ext_net = router['external_gateway_info']['network_id']
                    for port in ports:
                        if port['device_id'] == router_id and port['network_id'] == ext_net:
                            ip_address = port['fixed_ips'][0]['ip_address']

        if ip_address:
            cmd = "route delete -net %s" % (subnet['cidr'])
            commands.getstatusoutput(cmd)
             
        return 1
    
    def create_keypair(self, name, public_key):
        keys = self.shell.nova.keypairs.findall(name=name)
        if keys:
            key = keys[0]
            # update key     
            if key.public_key != public_key:
                self.delete_keypair(key.id)
                key = self.shell.nova.keypairs.create(name=name, public_key=public_key)
        else:
            key = self.shell.nova.keypairs.create(name=name, public_key=public_key)
        return key

    def delete_keypair(self, id):
        keys = self.shell.nova.keypairs.findall(id=id)
        for key in keys:
            self.shell.nova.keypairs.delete(key) 
        return 1

    def get_private_networks(self, tenant=None):
        if not tenant:
            tenant = self.shell.nova.tenant
        tenant = self.shell.keystone.tenants.find(name=tenant)
        search_opts = {"tenant_id": tenant.id, "shared": False}
        private_networks = self.shell.quantum.list_networks(**search_opts)
        return private_networks

    def get_shared_networks(self):
        search_opts = {"shared": True}
        shared_networks = self.shell.quantum.list_networks(**search_opts)
        return shared_networks

    def get_network_subnet(self, network_id):
        subnet_id = None
        subnet = None
        if network_id:
            os_networks = self.shell.quantum.list_networks(id=network_id)["networks"]
            if os_networks:
                os_network = os_networks[0]
                if os_network['subnets']:
                    subnet_id = os_network['subnets'][0]
                    os_subnets = self.shell.quantum.list_subnets(id=subnet_id)['subnets']
                    if os_subnets:
                        subnet = os_subnets[0]['cidr']

        return (subnet_id, subnet)

    def spawn_instance(self, name, key_name=None, availability_zone=None, hostname=None, image_id=None, security_group=None, pubkeys=[], nics=None, metadata=None, userdata=None, flavor_name=None):
        if not flavor_name:
            flavor_name = self.config.nova_default_flavor

        flavor = self.shell.nova.flavors.find(name=flavor_name)

        if not security_group:
            security_group = self.config.nova_default_security_group

        files = {}
        #if pubkeys:
        #    files["/root/.ssh/authorized_keys"] = "\n".join(pubkeys).encode('base64')
        hints = {}
        
        # determine availability zone and compute host 
        availability_zone_filter = None
        if availability_zone is None or not availability_zone:
            availability_zone_filter = 'nova'
        else: 
            availability_zone_filter = availability_zone
        if hostname:
            availability_zone_filter += ':%s' % hostname

        server = self.shell.nova.servers.create(
                                            name=name,
                                            key_name = key_name,
                                            flavor=flavor.id,
                                            image=image_id,
                                            security_group = security_group,
                                            #files = files,
                                            scheduler_hints=hints,
                                            availability_zone=availability_zone_filter,
                                            nics=nics,
                                            networks=nics,
                                            meta=metadata,
                                            userdata=userdata)
        return server

    def destroy_instance(self, id):
        if (self.shell.nova.tenant=="admin"):
            # findall() is implemented as a list() followed by a python search of the
            # list. Since findall() doesn't accept "all_tenants", we do this using
            # list() ourselves. This allows us to delete an instance as admin.
            servers = self.shell.nova.servers.list(search_opts={"all_tenants": True})
        else:
            servers = self.shell.nova.servers.list()
        for server in servers:
            if server.id == id:
                result=self.shell.nova.servers.delete(server)

    def update_instance_metadata(self, id, metadata):
        servers = self.shell.nova.servers.findall(id=id)
        for server in servers:
            self.shell.nova.servers.set_meta(server, metadata)
            # note: set_meta() returns a broken Server() object. Don't try to
            # print it in the shell or it will fail in __repr__.

    def delete_instance_metadata(self, id, metadata):
        # note: metadata is a dict. Only the keys matter, not the values.
        servers = self.shell.nova.servers.findall(id=id)
        for server in servers:
            self.shell.nova.servers.delete_meta(server, metadata)

