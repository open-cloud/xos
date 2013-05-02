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
    has_openstack = False

def require_enabled(callable):
    enabled = Config().api_nova_enabled
    def wrapper(*args, **kwds):
        if enabled and has_openstack:
            return callable(*args, **kwds)
        else:
            return None
    return wrapper


class OpenStackManager:

    def __init__(self, auth={}, caller=None):
        self.client = None
        if auth:
            self.client = OpenStackClient(**auth)
        
        self.driver = OpenStackDriver(client=self.client) 
        self.caller=None

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


