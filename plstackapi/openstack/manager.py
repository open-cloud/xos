from plstackapi.planetstack import settings
from django.core import management
management.setup_environ(settings)
try:
    from plstackapi.openstack.client import OpenStackClient
    from plstackapi.openstack.driver import OpenStackDriver
    from plstackapi.planetstack.config import Config
    from plstackapi.core.models import * 
    has_openstack = True
except:
    has_openpstack = False

manager_enabled = Config().api_nova_enabled

def require_enabled(callable):
    def wrapper(*args, **kwds):
        if manager_enabled and has_openstack:
            return callable(*args, **kwds)
        else:
            return None
    return wrapper


class OpenStackManager:

    def __init__(self, auth={}, caller=None):
        self.client = None
        self.driver = None
        self.caller = None
        self.has_openstack = has_openstack       
        self.enabled = manager_enabled

        if has_openstack and manager_enabled:
            if auth:
                self.client = OpenStackClient(**auth)
            else:
                self.client = OpenStackClient()
            self.driver = OpenStackDriver(client=self.client) 
            
            if caller:
                self.caller = caller:
            else:
                self.caller = self.driver.admin_user
                self.caller.user_id = self.caller.id 

    @require_enabled
    def save_role(self, role):
        if not role.role_id:
            keystone_role = self.driver.create_role(role.role_type)
            role.role_id = keystone_role.id

    @require_enabled
    def delete_role(self, role):
        if role.role_id:
            self.driver.delete_role({'id': role.role_id})

    @require_enabled
    def save_key(self, key):
        if not key.key_id:
            key_fields = {'name': key.name,
                          'key': key.key}
            nova_key = self.driver.create_keypair(**key_fields)
            key.key_id = nova_key.id        

    @require_enabled
    def delete_key(self, key):
        if key.key_id:
            self.driver.delete_keypair(key.key_id)

    @require_enabled
    def save_user(self, user):
        if not user.user_id:
            name = user.email[:user.email.find('@')]
            user_fields = {'name': name,
                           'email': user.email,
                           'password': user.password,
                           'enabled': True}
            keystone_user = self.driver.create_user(**user_fields)
            user.user_id = keystone_user.id
    
    @require_enabled
    def delete_user(self, user):
        if user.user_id:
            self.driver.delete_user(user.user_id)        
    

    
    @require_enabled
    def save_site(self, site, add_role=True):
        if not site.tenant_id:
            tenant = self.driver.create_tenant(tenant_name=site.login_base,
                                               description=site.name,
                                               enabled=site.enabled)
            site.tenant_id = tenant.id
            # give caller an admin role at the tenant they've created
            self.driver.add_user_role(self.caller.user_id, tenant.id, 'admin')

        # update the record
        if site.id and site.tenant_id:
            self.driver.update_tenant(site.tenant_id,
                                      description=site.name,
                                      enabled=site.enabled)

    @require_enabled
    def delete_site(self, site):
        if site.tenant_id:
            self.driver.delete_tenant(site.tenant_id)
               
    @require_enabled
    def save_slice(self, slice):
        if not slice.tenant_id:
            nova_fields = {'tenant_name': slice.name,
                   'description': slice.description,
                   'enabled': slice.enabled}
            tenant = self.driver.create_tenant(**nova_fields)
            slice.tenant_id = tenant.id

            # give caller an admin role at the tenant they've created
            self.driver.add_user_role(self.caller.user_id, tenant.id, 'admin')

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

        if slice.id and slice.tenant_id:
            self.driver.update_tenant(slice.tenant_id,
                                      description=slice.description,
                                      enabled=slice.enabled)    

    @require_enabled
    def delete_slice(self, slice):
        if slice.tenant_id:
            self.driver.delete_router(slice.router_id)
            self.driver.delete_network(slice.network_id)
            self.driver.delete_tenant(slice.tenant_id)

    @require_enabled
    def save_subnet(self, subnet):    
        if not subnet.subnet_id:
            quantum_subnet = self.driver.create_subnet(name= subnet.slice.name,
                                          network_id=subnet.slice.network_id,
                                          cidr_ip = subnet.cidr,
                                          ip_version=subnet.ip_version,
                                          start = subnet.start,
                                          end = subnet.end)
            subnet.subnet_id = quantum_subnet['id']
            # add subnet as interface to slice's router
            self.driver.add_router_interface(subnet.slice.router_id, subnet.subnet_id)
            #add_route = 'route add -net %s dev br-ex gw 10.100.0.5' % self.cidr
            #commands.getstatusoutput(add_route)

    
    @require_enabled
    def delete_subnet(self, subnet):
        if subnet.subnet_id:
            self.driver.delete_router_interface(subnet.slice.router_id, subnet.subnet_id)
            self.driver.delete_subnet(subnet.subnet_id)
            #del_route = 'route del -net %s' % self.cidr
            #commands.getstatusoutput(del_route)
    
    @require_enabled
    def save_sliver(self, sliver):
        if not sliver.instance_id:
            instance = self.driver.spawn_instance(name=sliver.name,
                                   key_name = sliver.key.name,
                                   image_id = sliver.image.image_id,
                                   hostname = sliver.node.name )
            sliver.instance_id = instance.id
            sliver.instance_name = getattr(instance, 'OS-EXT-SRV-ATTR:instance_name')

    @require_enabled
    def delete_sliver(self, sliver):
        if sliver.instance_id:
            self.driver.destroy_instance(sliver.instance_id) 
    

    def refresh_nodes(self):
        # collect local nodes
        nodes = Node.objects.all()
        nodes_dict = {}
        for node in nodes:
            if 'viccidev10' not in node.name:
                nodes_dict[node.name] = node 
        
        deployment = DeploymentNetwork.objects.filter(name='VICCI')[0]
        login_bases = ['princeton', 'stanford', 'gt', 'uw', 'mpisws']
        sites = Site.objects.filter(login_base__in=login_bases)
        # collect nova nodes:
        compute_nodes = self.client.nova.hypervisors.list()

        compute_nodes_dict = {}
        for compute_node in compute_nodes:
            compute_nodes_dict[compute_node.hypervisor_hostname] = compute_node

        # add new nodes:
        new_node_names = set(compute_nodes_dict.keys()).difference(nodes_dict.keys())
        i = 0
        max = len(sites)
        for name in new_node_names:
            if i == max:
                i = 0
            site = sites[i]
            node = Node(name=compute_nodes_dict[name].hypervisor_hostname,
                        site=site,
                        deploymentNetwork=deployment)
            node.save()
            i+=1

        # remove old nodes
        old_node_names = set(nodes_dict.keys()).difference(compute_nodes_dict.keys())
        Node.objects.filter(name__in=old_node_names).delete()

    def refresh_images(self):
        # collect local images
        images = Image.objects.all()
        images_dict = {}    
        for image in images:
            images_dict[image.name] = image

        # collect glance images
        glance_images = self.client.glance.get_images()
        glance_images_dict = {}
        for glance_image in glance_images:
            glance_images_dict[glance_image['name']] = glance_image

        # add new images
        new_image_names = set(glance_images_dict.keys()).difference(images_dict.keys())
        for name in new_image_names:
            image = Image(image_id=glance_images_dict[name]['id'],
                          name=glance_images_dict[name]['name'],
                          disk_format=glance_images_dict[name]['disk_format'],
                          container_format=glance_images_dict[name]['container_format'])
            image.save()

        # remove old images
        old_image_names = set(images_dict.keys()).difference(glance_images_dict.keys())
        Image.objects.filter(name__in=old_image_names).delete()


