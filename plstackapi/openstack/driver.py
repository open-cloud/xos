from plstackapi.planetstack.config import Config
from plstackapi.openstack.shell import OpenStackShell

class OpenStackDriver:

    def __init__(self, config = None): 
        if config:
            self.config = Config(config)
        else:
            self.config = Config() 
        self.shell = OpenStackShell()


    def spawn_instances(self, name, key_name, hostnames=[], flavor=None, image=None, security_group=None, pubkeys=[]):
        if not flavor:
            flavor = self.config.nova_default_flavor
        if not image:
            image = self.config.nova_default_imave
        if not security_group:
            security_group = self.config.nova_default_security_group 

        authorized_keys = "\n".join(pubkeys)
        files = {'/root/.ssh/authorized_keys': authorized_keys}
       
        for hostname in hostnames:
            flavor_id = self.shell.nova.flavors.find(name=flavor)
            images = self.shell.glance.get_images(name=image)
            if not images:
                raise Exception, "Image not found: " + image  
            image_id = images[0]['id']
            hints = {'force_hosts': hostname}
            server = self.shell.nova.servers.create(
                                                name=name,
                                                key_name = key_name,
                                                flavor=flavor_id,
                                                image=image_id,
                                                security_group = security_group,
                                                files=files,
                                                scheduler_hints=hints)
          
    def destroy_instances(self, name, hostnames=[]):
        servers = self.shell.nova.servers.list()
        for server in servers:
            hostname = server._info['OS-EXT-SRV-ATTR:host']
            if name == server.name and hostname in hostnames:
                self.shell.nova.servers.delete(server)
