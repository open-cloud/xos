import os
import base64
import traceback
from collections import defaultdict
from django.db.models import F, Q
from planetstack.config import Config
from util.logger import Logger, logging
from observer.openstacksyncstep import OpenStackSyncStep
from core.models import *

logger = Logger(logfile='/var/log/observer.log', level=logging.INFO)

class GarbageCollector(OpenStackSyncStep):
    requested_interval = 86400
    provides=[]

    def call(self, **args):
        try:
            self.gc_networks()
            #self.gc_user_tenant_roles()
            #self.gc_tenants()
            #self.gc_users()
            self.gc_slivers()
            #self.gc_sliver_ips()
            pass 
        except:
            traceback.print_exc()

    def gc_networks(self):
        """
        Remove all neutron networks that do not exist in the planetstack db.
        """ 
        # some networks cannot be deleted
        system_networks = ['nat-net','private-admin']
        for network_template in NetworkTemplate.objects.all():
            if network_template.sharedNetworkName and \
              network_template.sharedNetworkName not in system_networks:
                system_networks.append(network_template.sharedNetworkName)

        networks = Network.objects.filter(enacted__isnull=False)
        networks_dict = {}
        for network in networks:
            networks_dict[network.name] = network  

        # some deployments are at the same url. Keep track of the urls we've visited
        # to make sure we aren't making redundant calls
        completed_urls = []
        for deployment in Deployment.objects.all():
            # skip deployments that we've already processed
            if deployment.auth_url in completed_urls:
                continue
            try:
                driver = self.driver.admin_driver(deployment=deployment)
                neutron_networks = driver.shell.quantum.list_networks()['networks']
                for neutron_network in neutron_networks:
                    # skip system networks
                    if neutron_network['name'] in system_networks:
                        continue         
                    if neutron_network['name'] not in networks_dict:
                        try:
                            logger.info("GarbageCollector: deleting network %s" % neutron_network['name'])
                            for subnet_id in neutron_network['subnets']:
                                driver.delete_subnet(subnet_id)
                            driver.delete_network(neutron_network['id'])
                        except:
                            logger.log_exc("GarbageCollector: delete network %s failed" % neutron_network['name'])
            except:
                logger.log_exc("GarbageCollector: Error at deployment %s" % deployment)
                                
            completed_urls.append(deployment.auth_url) 

    def gc_tenants(self):
        """
        Remove sites and slices that no don't exist in openstack db if they 
        have an enacted time (enacted != None).
        """ 
        # some tenants cannot be deleted
        system_tenants = ['admin','service', 'invisible_to_admin']
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
        # some deployments are at the same url. Keep track of the urls we've visited
        # to make sure we aren't making redundant calls
        completed_urls = []
        for deployment in Deployment.objects.all():
            # skip deployments that we've already processed
            if deployment.auth_url in completed_urls:
                continue

            driver = self.driver.admin_driver(deployment=deployment)
            tenants = driver.shell.keystone.tenants.findall()
            for tenant in tenants:
                if tenant.name in system_tenants: 
                    continue
                if tenant.name not in site_dict and tenant.name not in slice_dict:
                    try:
                        logger.info("GarbageCollector: deleting tenant: %s" % (tenant))
                        driver.delete_tenant(tenant.id)
                    except:
                        logger.log_exc("GarbageCollector: delete tenant failed: %s" % tenant)
            completed_urls.append(deployment.auth_url)

    def gc_users(self):
        """
        Remove users that do not exist in openstack db if they have an 
        enacted time (enacted != None).
        """ 
        # some users cannot be deleted
        system_users = ['admin', 'nova', 'quantum', 'neutron' 'glance', \
                        'cinder', 'swift', 'service', 'demo']
    
        # get all users that where enacted != null. We can assume these users
        # have previously been synced and need to be checed for deletion.
        users = User.objects.filter(enacted__isnull=False)
        user_dict = {}
        for user in users:
            user_dict[user.kuser_id] = user

        # delete keystone users that don't have a user record
        # some deployments are at the same url. Keep track of the urls we've visited
        # to make sure we aren't making redundant calls
        completed_urls = []
        for deployment in Deployment.objects.all():
            # skip deployments that we've already processed
            if deployment.auth_url in completed_urls:
                continue

            driver = self.driver.admin_driver(deployment=deployment)
            users = driver.shell.keystone.users.findall()
            for user in users:
                if user.name in system_users:
                    continue
                if user.id not in user_dict:
                    try:
                        logger.info("GarbageCollector: deleting user: %s" % user)
                        self.driver.delete_user(user.id)
                    except:
                        logger.log_exc("GarbageCollector: delete user failed: %s" % user)
            completed_urls.append(deployment.auth_url)          

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

        # some deployments are at the same url. Keep track of the urls we've visited
        # to make sure we aren't making redundant calls
        completed_urls = [] 
        # Some user tenant role aren't stored in planetstack but they must be preserved. 
        # Role that fall in this category are
        # 1. Never remove a user's role that their home site
        # 2. Never remove a user's role at a slice they've created.
        # Keep track of all roles that must be preserved.     
        users = User.objects.all()
        for deployment in Deployment.objects.all():
            # skip deployments that we've already processed
            if deployment.auth_url in completed_urls:
                continue

            driver = self.driver.admin_driver(deployment=deployment)
            tenants = driver.shell.keystone.tenants.list() 
            for user in users:
                # skip admin roles
                if user.kuser_id == self.driver.admin_user.id:
                    continue
     
                ignore_tenant_ids = []
                k_user = driver.shell.keystone.users.find(id=user.kuser_id)
                ignore_tenant_ids = [s['tenant_id'] for s in user.slices.values()]
                if user.site:
                    ignore_tenant_ids.append(user.site.tenant_id) 

                # get user roles in keystone
                for tenant in tenants:
                    # skip preserved tenant ids
                    if tenant.tenant_id in ignore_tenant_ids: 
                        continue          
                    # compare user tenant roles
                    user_tenant_role_ids = user_tenant_roles.get((user.kuser_id, tenant.id), [])

                    if user_tenant_role_ids:
                        # The user has roles at the tenant. Check if roles need to 
                        # be updated.
                        k_user_roles =  driver.shell.keystone.roles.roles_for_user(k_user, tenant)
                        for k_user_role in k_user_roles:
                            if k_user_role.role_id not in user_tenant_role_ids: 
                                logger.info("GarbageCollector: removing user role %s for %s at %s" % \
                                           (k_user_role, k_user.username, tenant.name))
                                driver.shell.keyston.remove_user_role(k_user, k_user_role, tenant) 
                    else:
                        # remove all roles the user has at the tenant. 
                        for k_user_role in k_user_roles:
                            logger.info("GarbageCollector: removing user role %s for %s at %s" % \
                                       (k_user_role, k_user.username, tenant.name))
                            driver.shell.keyston.remove_user_role(k_user, k_user_role, tenant)
            completed_urls.append(deployment.auth_url) 
 
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

        
        # some deployments are at the same url. Keep track of the urls we've visited
        # to make sure we aren't making redundant calls
        completed_urls = []
        for deployment in Deployment.objects.all():
            # skip deployments that we've already processed
            if deployment.auth_url in completed_urls:
                continue

            try:
                driver = self.driver.admin_driver(deployment=deployment)
                for tenant in driver.shell.keystone.tenants.list():
                    if tenant.name in ['admin', 'services']:
                        continue
                    # delete sliver that don't have a sliver record
                    tenant_driver = self.driver.client_driver(tenant=tenant.name, deployment=deployment)
                    for instance in tenant_driver.shell.nova.servers.list():
                        if instance.id not in sliver_dict:
                            try:
                                logger.info("GarbageCollector: destroying sliver: %s %s" % (instance, instance.id))
                                tenant_driver.destroy_instance(instance.id)
                            except:
                                logger.log_exc("GarbageCollector: destroy sliver failed: %s" % instance)
            except:
                logger.log_exc("GarbageCollector: Error at deployment %s" % deployment) 
            completed_urls.append(deployment.auth_url)
               

    def gc_sliver_ips(self):
        """
        Update ips that have changed.
        """
        # fill in null ip addresses
        slivers = Sliver.objects.filter(ip=None)
        for sliver in slivers:
            # update connection
            
            driver = self.driver.client_driver(tenant=sliver.slice.name, deployment=sliver.node.deployment)
            servers = driver.shell.nova.servers.findall(id=sliver.instance_id)
            if not servers:
                continue
            server = servers[0]
            ips = server.addresses.get(sliver.slice.name, [])
            if ips and sliver.ip != ips[0]['addr']:
                sliver.ip = ips[0]['addr']
                sliver.save()
                logger.info("updated sliver ip: %s %s" % (sliver, ips[0]))

    def gc_nodes(self):
         # collect local nodes
        nodes = Node.objects.all()
        nodes_dict = {}
        for node in nodes:
            nodes_dict[node.name] = node

        # collect nova nodes:
        compute_nodes_dict = {}
        for deployment in Deployment.objets.all():
            driver = self.driver.admin_driver(deployment=deployment) 
            compute_nodes = driver.nova.hypervisors.list()
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
        glance_images_dict = {}
        for deployment in Deployment.objects.all():
            driver = self.driver.admin_driver(deployment=deployment)
            glance_images = driver.shell.glance.get_images()
            for glance_image in glance_images:
                glance_images_dict[glance_image['name']] = glance_image

        # remove old images
        old_image_names = set(images_dict.keys()).difference(glance_images_dict.keys())
        Image.objects.filter(name__in=old_image_names).delete()
