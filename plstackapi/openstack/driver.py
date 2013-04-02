from plstackapi.planetstack.config import Config
from plstackapi.openstack.shell import OpenStackShell

class OpenStackDriver:

    def __init__(self, config = None): 
        if config:
            self.config = Config(config)
        else:
            self.config = Config() 
        self.shell = OpenStackShell()

    def create_tenant(self, **kwds):
        """Create keystone tenant. Suggested fields: name, description, enabled"""  
        required_fields = ['tenant_name', 'enabled', 'description']
        for field in required_fields:
            if field not in kwds:
                raise Exception, "Must specify %s" % field

        tenants = self.shell.keystone.tenants.findall(name=kwds['name'])
        if not tenants:
            tenant = self.shell.keystone.tenants.create(**kwds)
        else:
            tenant = tenants[0]
        return tenant

    def update_tenant(self, id, **kwds):
        return self.shell.keystone.tenants.update(self.id, **kwds)

    def delete_tenant(self, id):
        tenant = self.shell.keystone.tenants.find(id=id)
        return self.shell.keystone.tenants.delete(tenant)
         

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
