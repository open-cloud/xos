import os
import base64
import traceback
from collections import defaultdict
from django.db.models import F, Q
from planetstack.config import Config
from util.logger import Logger, logging
from observer.openstacksyncstep import OpenStackSyncStep
from core.models import *

logger = Logger(level=logging.INFO)

class GarbageCollector(OpenStackSyncStep):
    requested_interval = 86400
    provides=[]

    def call(self, **args):
        try:
            #self.gc_roles()
            self.gc_tenants()
            self.gc_users()
            self.gc_user_tenant_roles()
            self.gc_slivers()
            self.gc_sliver_ips()
            self.gc_external_routes()
        except:
            traceback.print_exc() 

    def gc_roles(self):
        """
         all role that don't already exist in keystone. Remove keystone roles that
        don't exist in planetstack
        """
        # sync all roles that don't already in keystone  
        keystone_roles = self.driver.shell.keystone.roles.findall()
        keystone_role_names = [kr.name for kr in keystone_roles]
        pending_roles = Role.objects.all()
        pending_role_names = [r.role_type for r in pending_roles] 
        # don't delete roles for now 
        """ 
        # delete keystone roles that don't exist in planetstack
        for keystone_role in keystone_roles:
            if keystone_role.name == 'admin':
                continue
            if keystone_role.name not in pending_role_names:
                try:
                    self.driver.delete_role({id: keystone_role.id})
                except:
                    traceback.print_exc()
        """

    def gc_tenants(self):
        """
        Remove sites and slices that no don't exist in openstack db if they 
        have an enacted time (enacted != None).
        """ 
        # get all sites that where enacted != null. We can assume these sites
        # have previously been synced and need to be checed for deletion.
        sites = Site.objects.filter(enacted__isnull=False)
        site_dict = {}
        for site in sites:
            site_dict[site.login_base] = site

        # get all slices that where enacted != null. We can assume these slices
        # have previously been synced and need to be checed for deletion.
        slices = Slice.objects.filter(enacted__isnull=False)
        slice_dict = {}
        for slice in slices:
            slice_dict[slice.name] = slice

        # delete keystone tenants that don't have a site record
        tenants = self.driver.shell.keystone.tenants.findall()
        system_tenants = ['admin','service', 'invisible_to_admin']
        for tenant in tenants:
            if tenant.name in system_tenants: 
                continue
            if tenant.name not in site_dict and tenant.name not in slice_dict:
                try:
                    self.driver.delete_tenant(tenant.id)
                    logger.info("deleted tenant: %s" % (tenant))
                except:
                    logger.log_exc("delete tenant failed: %s" % tenant)


    def gc_users(self):
        """
        Remove users that no don't exist in openstack db if they have an 
        enacted time (enacted != None).
        """ 
        # get all users that where enacted != null. We can assume these users
        # have previously been synced and need to be checed for deletion.
        users = User.objects.filter(enacted__isnull=False)
        user_dict = {}
        for user in users:
            user_dict[user.kuser_id] = user

        # delete keystone users that don't have a user record
        system_users = ['admin', 'nova', 'quantum', 'glance', 'cinder', 'swift', 'service', 'demo']
        users = self.driver.shell.keystone.users.findall()
        for user in users:
            if user.name in system_users:
                continue
            if user.id not in user_dict:
                try:
                    self.driver.delete_user(user.id)
                    logger.info("deleted user: %s" % user)
                except:
                    logger.log_exc("delete user failed: %s" % user)
                    

    def gc_user_tenant_roles(self):
        """
        Remove roles that don't exist in openstack db if they have 
        an enacted time (enacted != None).
        """
        # get all site privileges and slice memberships that have been enacted 
        user_tenant_roles = defaultdict(list)
        for site_priv in SitePrivilege.objects.filter(enacted__isnull=False):
            user_tenant_roles[(site_priv.user.kuser_id, site_priv.site.tenant_id)].append(site_priv.role.role)
        for slice_memb in SlicePrivilege.objects.filter(enacted__isnull=False):
            user_tenant_roles[(slice_memb.user.kuser_id, slice_memb.slice.tenant_id)].append(slice_memb.role.role)  
 
        # Some user tenant role aren't stored in planetstack but they must be preserved. 
        # Role that fall in this category are
        # 1. Never remove a user's role that their home site
        # 2. Never remove a user's role at a slice they've created.
        # Keep track of all roles that must be preserved.     
        users = User.objects.all()
        preserved_roles = {}
        for user in users:
            tenant_ids = [s['tenant_id'] for s in user.slices.values()]
            if user.site:
                tenant_ids.append(user.site.tenant_id) 
            preserved_roles[user.kuser_id] = tenant_ids

 
        # begin removing user tenant roles from keystone. This is stored in the 
        # Metadata table.
        for metadata in self.driver.shell.keystone_db.get_metadata():
            # skip admin roles
            if metadata.user_id == self.driver.admin_user.id:
                continue
            # skip preserved tenant ids
            if metadata.user_id in preserved_roles and \
               metadata.tenant_id in preserved_roles[metadata.user_id]: 
                continue           
            # get roles for user at this tenant
            user_tenant_role_ids = user_tenant_roles.get((metadata.user_id, metadata.tenant_id), [])

            if user_tenant_role_ids:
                # The user has roles at the tenant. Check if roles need to 
                # be updated.
                user_keystone_role_ids = metadata.data.get('roles', [])
                for role_id in user_keystone_role_ids:
                    if role_id not in user_tenant_role_ids: 
                        user_keystone_role_ids.pop(user_keystone_role_ids.index(role_id))
            else:
                # The user has no roles at this tenant. 
                metadata.data['roles'] = [] 
            #session.add(metadata)
            logger.info("pruning metadata for %s at %s" % (metadata.user_id, metadata.tenant_id))
 
    def gc_slivers(self):
        """
        Remove slivers that no don't exist in openstack db if they have 
        an enacted time (enacted != None).
        """
        # get all slivers where enacted != null. We can assume these users
        # have previously been synced and need to be checed for deletion.
        slivers = Sliver.objects.filter(enacted__isnull=False)
        sliver_dict = {}
        for sliver in slivers:
            sliver_dict[sliver.instance_id] = sliver

        # delete sliver that don't have a sliver record
        ctx = self.driver.shell.nova_db.ctx 
        instances = self.driver.shell.nova_db.instance_get_all(ctx)
        for instance in instances:
            if instance.uuid not in sliver_dict:
                try:
                    # lookup tenant and update context  
                    tenant = self.driver.shell.keystone.tenants.find(id=instance.project_id)
                    driver = self.driver.client_driver(tenant=tenant.name) 
                    driver.destroy_instance(instance.uuid)
                    logger.info("destroyed sliver: %s" % (instance))
                except:
                    logger.log_exc("destroy sliver failed: %s" % instance) 
                

    def gc_sliver_ips(self):
        """
        Update ips that have changed.
        """
        # fill in null ip addresses
        slivers = Sliver.objects.filter(ip=None)
        for sliver in slivers:
            # update connection
            driver = self.driver.client_driver(tenant=sliver.slice.name)
            servers = driver.shell.nova.servers.findall(id=sliver.instance_id)
            if not servers:
                continue
            server = servers[0]
            ips = server.addresses.get(sliver.slice.name, [])
            if ips and sliver.ip != ips[0]['addr']:
                sliver.ip = ips[0]['addr']
                sliver.save()
                logger.info("updated sliver ip: %s %s" % (sliver, ips[0]))

    def gc_external_routes(self):
        pass

    def gc_nodes(self):
         # collect local nodes
        nodes = Node.objects.all()
        nodes_dict = {}
        for node in nodes:
            nodes_dict[node.name] = node

        # collect nova nodes:
        compute_nodes = self.client.nova.hypervisors.list()
        compute_nodes_dict = {}
        for compute_node in compute_nodes:
            compute_nodes_dict[compute_node.hypervisor_hostname] = compute_node

        # remove old nodes
        old_node_names = set(nodes_dict.keys()).difference(compute_nodes_dict.keys())
        Node.objects.filter(name__in=old_node_names).delete()

    def gc_images(self):
        # collect local images
        images = Image.objects.all()
        images_dict = {}
        for image in images:
            images_dict[image.name] = image

        # collect glance images
        glance_images = self.driver.shell.glance.get_images()
        glance_images_dict = {}
        for glance_image in glance_images:
            glance_images_dict[glance_image['name']] = glance_image

        # remove old images
        old_image_names = set(images_dict.keys()).difference(glance_images_dict.keys())
        Image.objects.filter(name__in=old_image_names).delete()
