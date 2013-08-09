import time
import traceback
import commands
import threading

from datetime import datetime
from collections import defaultdict
from core.models import *
from django.db.models import F, Q
from openstack.manager import OpenStackManager
from util.logger import Logger, logging, logger
#from timeout import timeout


logger = Logger(logfile='observer.log', level=logging.INFO)

class OpenStackObserver:
    
    def __init__(self):
        self.manager = OpenStackManager()
        # The Condition object that gets signalled by Feefie events
        self.event_cond = threading.Condition()

    def wait_for_event(self, timeout):
        self.event_cond.acquire()
        self.event_cond.wait(timeout)
        self.event_cond.release()
        
    def wake_up(self):
        logger.info('Wake up routine called. Event cond %r'%self.event_cond)
        self.event_cond.acquire()
        self.event_cond.notify()
        self.event_cond.release()

    def run(self):
        if not self.manager.enabled or not self.manager.has_openstack:
            return
        while True:
            try:
                logger.info('Observer run loop')
                #self.sync_roles()

                logger.info('Calling sync tenants')
                try:
                    self.sync_tenants()
                except:
                    logger.log_exc("Exception in sync_tenants")
                    traceback.print_exc()

                logger.info('Calling sync users')
                try:
                    self.sync_users()
                except:
                    logger.log_exc("Exception in sync_users")
                    traceback.print_exc()

                logger.info('Calling sync tenant roles')
                try:
                    self.sync_user_tenant_roles()
                except:
                    logger.log_exc("Exception in sync_users")
                    traceback.print_exc()

                logger.info('Calling sync slivers')
                try:
                    self.sync_slivers()
                except:
                    logger.log_exc("Exception in sync slivers")
                    traceback.print_exc()

                logger.info('Calling sync sliver ips')
                try:
                    self.sync_sliver_ips()
                except:
                    logger.log_exc("Exception in sync_sliver_ips")
                    traceback.print_exc()

                logger.info('Calling sync networks')
                try:
                    self.sync_networks()
                except:
                    logger.log_exc("Exception in sync_networks")
                    traceback.print_exc()

                logger.info('Calling sync external routes')
                try:
                    self.sync_external_routes()
                except:
                     logger.log_exc("Exception in sync_external_routes")
                     traceback.print_exc()

                logger.info('Waiting for event')
                self.wait_for_event(timeout=300)
                time.sleep(300)
                logger.info('Observer woken up')
            except:
                logger.log_exc("Exception in observer run loop")
                traceback.print_exc()

    def sync_roles(self):
        """
        save all role that don't already exist in keystone. Remove keystone roles that
        don't exist in planetstack
        """
        # sync all roles that don't already in keystone  
        keystone_roles = self.manager.driver.shell.keystone.roles.findall()
        keystone_role_names = [kr.name for kr in keystone_roles]
        pending_roles = Role.objects.all()
        pending_role_names = [r.role_type for r in pending_roles] 
        for role in pending_roles:
            if role.role_type not in keystone_role_names:
                try:
                    self.manager.save_role(role)
                    logger.info("save role: %s" % (role))
                except:
                    logger.log_exc("save role failed: %s" % role)  
                    traceback.print_exc()

        # don't delete roles for now 
        """ 
        # delete keystone roles that don't exist in planetstack
        for keystone_role in keystone_roles:
            if keystone_role.name == 'admin':
                continue
            if keystone_role.name not in pending_role_names:
                try:
                    self.manager.driver.delete_role({id: keystone_role.id})
                except:
                    traceback.print_exc()
        """

    def sync_tenants(self):
        """
        Save all sites and sliceswhere enacted < updated or enacted == None. 
        Remove sites and slices that no don't exist in openstack db if they 
        have an enacted time (enacted != None).
        """ 
        # get all sites that need to be synced (enacted < updated or enacted is None)
        pending_sites = Site.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))
        for site in pending_sites:
            try:
                self.manager.save_site(site)
                logger.info("saved site %s" % site)
            except:
                logger.log_exc("save site failed: %s" % site)

        # get all slices that need to be synced (enacted < updated or enacted is None)
        pending_slices = Slice.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))
        for slice in pending_slices:
            try:
                self.manager.init_caller(slice.creator, slice.creator.site.login_base)
                self.manager.save_slice(slice)
                logger.info("saved slice %s" % slice)
            except:
                logger.log_exc("save slice failed: %s" % slice)

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
        tenants = self.manager.driver.shell.keystone.tenants.findall()
        system_tenants = ['admin','service']
        for tenant in tenants:
            if tenant.name in system_tenants: 
                continue
            if tenant.name not in site_dict and tenant.name not in slice_dict:
                try:
                    self.manager.driver.delete_tenant(tenant.id)
                    logger.info("deleted tenant: %s" % (tenant))
                except:
                    logger.log_exc("delete tenant failed: %s" % tenant)


    def sync_users(self):
        """
        save all users where enacted < updated or enacted == None. Remove users that
        no don't exist in openstack db if they have an enacted time (enacted != None).
        """ 
        # get all users that need to be synced (enacted < updated or enacted is None)
        pending_users = User.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))
        for user in pending_users:
            try:
                self.manager.save_user(user)
                logger.info("saved user: %s" % (user))
            except:
                logger.log_exc("save user failed: %s" %user)

        # get all users that where enacted != null. We can assume these users
        # have previously been synced and need to be checed for deletion.
        users = User.objects.filter(enacted__isnull=False)
        user_dict = {}
        for user in users:
            user_dict[user.kuser_id] = user

        # delete keystone users that don't have a user record
        system_users = ['admin', 'nova', 'quantum', 'glance', 'cinder', 'swift', 'service']
        users = self.manager.driver.shell.keystone.users.findall()
        for user in users:
            if user.name in system_users:
                continue
            if user.id not in user_dict:
                try:
                    #self.manager.driver.delete_user(user.id)
                    logger.info("deleted user: %s" % user)
                except:
                    logger.log_exc("delete user failed: %s" % user)
                    

    def sync_user_tenant_roles(self):
        """
        Save all site privileges and slice memberships wheree enacted < updated or 
        enacted == None. Remove ones that don't exist in openstack db if they have 
        an enacted time (enacted != None).
        """
        # sync site privileges
        pending_site_privileges = SitePrivilege.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))
        for site_priv in pending_site_privileges:
            try:
                self.manager.save_site_privilege(site_priv)  
                logger.info("saved site privilege: %s" % (site_priv))
            except: logger.log_exc("save site privilege failed: %s " % site_priv)

        # sync slice memberships
        pending_slice_memberships = SliceMembership.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))
        for slice_memb in pending_slice_memberships:
            try:
                self.manager.save_slice_membership(slice_memb)
                logger.info("saved slice membership: %s" % (slice_memb))
            except: logger.log_exc("save slice membership failed: %s" % slice_memb)

        # get all site privileges and slice memberships that have been enacted 
        user_tenant_roles = defaultdict(list)
        for site_priv in SitePrivilege.objects.filter(enacted__isnull=False):
            user_tenant_roles[(site_priv.user.kuser_id, site_priv.site.tenant_id)].append(site_priv.role.role)
        for slice_memb in SliceMembership.objects.filter(enacted__isnull=False):
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
            tenant_ids.append(user.site.tenant_id) 
            preserved_roles[user.kuser_id] = tenant_ids

 
        # begin removing user tenant roles from keystone. This is stored in the 
        # Metadata table.
        for metadata in self.manager.driver.shell.keystone_db.get_metadata():
            # skip admin roles
            if metadata.user_id == self.manager.driver.admin_user.id:
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
 
    def sync_slivers(self):
        """
        save all slivers where enacted < updated or enacted == None. Remove slivers that
        no don't exist in openstack db if they have an enacted time (enacted != None).
        """
        # get all users that need to be synced (enacted < updated or enacted is None)
        pending_slivers = Sliver.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))
        for sliver in pending_slivers:
            if sliver.creator: 
                try: 
                    # update manager context
                    self.manager.init_caller(sliver.creator, sliver.slice.name)
                    self.manager.save_sliver(sliver)
                    logger.info("saved sliver: %s" % (sliver))
                except:
                    logger.log_exc("save sliver failed: %s" % sliver) 

        # get all slivers where enacted != null. We can assume these users
        # have previously been synced and need to be checed for deletion.
        slivers = Sliver.objects.filter(enacted__isnull=False)
        sliver_dict = {}
        for sliver in slivers:
            sliver_dict[sliver.instance_id] = sliver

        # delete sliver that don't have a sliver record
        ctx = self.manager.driver.shell.nova_db.ctx 
        instances = self.manager.driver.shell.nova_db.instance_get_all(ctx)
        for instance in instances:
            if instance.uuid not in sliver_dict:
                try:
                    # lookup tenant and update context  
                    tenant = self.manager.driver.shell.keystone.tenants.find(id=instance.project_id) 
                    self.manager.init_admin(tenant=tenant.name)  
                    self.manager.driver.destroy_instance(instance.uuid)
                    logger.info("destroyed sliver: %s" % (instance))
                except:
                    logger.log_exc("destroy sliver failed: %s" % instance) 
                

    def sync_sliver_ips(self):
        # fill in null ip addresses
        slivers = Sliver.objects.filter(ip=None)
        for sliver in slivers:
            # update connection
            self.manager.init_admin(tenant=sliver.slice.name)
            servers = self.manager.driver.shell.nova.servers.findall(id=sliver.instance_id)
            if not servers:
                continue
            server = servers[0]
            ips = server.addresses.get(sliver.slice.name, [])
            if not ips:
                continue
            sliver.ip = ips[0]['addr']
            sliver.save()
            logger.info("saved sliver ip: %s %s" % (sliver, ips[0]))

    def sync_external_routes(self):
        routes = self.manager.driver.get_external_routes() 
        subnets = self.manager.driver.shell.quantum.list_subnets()['subnets']
        for subnet in subnets:
            try:
                self.manager.driver.add_external_route(subnet, routes)
            except:
                logger.log_exc("failed to add external route for subnet %s" % subnet)

    def sync_networks(self):
        """
        save all networks where enacted < updated or enacted == None. Remove networks that
        no don't exist in openstack db if they have an enacted time (enacted != None).
        """
        # get all users that need to be synced (enacted < updated or enacted is None)
        pending_networks = Network.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))
        for network in pending_networks:
            if network.owner and network.owner.creator:
                try:
                    # update manager context
                    self.manager.init_caller(network.owner.creator, network.owner.name)
                    self.manager.save_network(network)
                    logger.info("saved network: %s" % (network))
                except:
                    logger.log_exc("save network failed: %s" % network)

        # get all networks where enacted != null. We can assume these users
        # have previously been synced and need to be checed for deletion.
        networks = Network.objects.filter(enacted__isnull=False)
        network_dict = {}
        for network in networks:
            network_dict[network.network_id] = network

        # TODO: delete Network objects if quantum network doesn't exist
        #       (need to write self.manager.driver.shell.quantum_db)

