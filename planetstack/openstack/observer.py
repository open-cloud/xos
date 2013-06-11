import time
import traceback
from datetime import datetime
from core.models import *
from django.db.models import F, Q
from openstack.manager import OpenStackManager


class OpenStackObserver:
    
    def __init__(self):
        self.manager = OpenStackManager()

    def run(self):
        if not self.manager.enabled or not self.manager.has_openstack:
            return
        while True:
            try:
                #self.sync_roles()
                self.sync_tenants()
                self.sync_users()
                #self.sync_user_tenant_roles()
                #self.sync_slivers()
                time.sleep(7)
            except:
                traceback.print_exc() 

    def sync_tenants(self):
        """
        Save all sites and sliceswhere enacted < updated or enacted == None. 
        Remove sites and slices that no don't exist in openstack db if they 
        have an enacted time (enacted != None).
        """ 
        # get all sites that need to be synced (enacted < updated or enacted is None)
        pending_sites = Site.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))
        for site in pending_sites:
            self.manager.save_site(site)
            site.enacted = datetime.now()
            site.save()

        # get all slices that need to be synced (enacted < updated or enacted is None)
        pending_slices = Slice.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))
        for slice in pending_slices:
            self.manager.save_slice(slice)
            slice.enacted = datetime.now()
            slice.save()

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
        for tenant in tenants:
            if tenant.name == 'admin': 
                continue
            if tenant.name not in site_dict and tenant.name not in slice_dict:
                #print "delete " + tenant.name
                pass
                #self.manager.driver.delete_tenant(tenant.id)


    def sync_users(self):
        """
        save all users where enacted < updated or enacted == None. Remove users that
        no don't exist in openstack db if they have an enacted time (enacted != None).
        """ 
        # get all users that need to be synced (enacted < updated or enacted is None)
        pending_users = User.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))
        for user in pending_users:
            self.manager.save_user(user)
            user.enacted = datetime.now()
            user.save()

        # get all users that where enacted != null. We can assume these users
        # have previously been synced and need to be checed for deletion.
        users = User.objects.filter(enacted__isnull=False)
        user_dict = {}
        for user in users:
            user_dict[user.kuser_id] = user

        # delete keystone users that don't have a user record
        users = self.manager.driver.shell.keystone.users.findall()
        for user in users:
            if user.name == 'admin':
                continue
            if user.id not in user_dict:
                pass
                #self.manager.driver.delete_user(user.id)
        
        
    def sync_slivers(self):
        """
        save all slivers where enacted < updated or enacted == None. Remove slivers that
        no don't exist in openstack db if they have an enacted time (enacted != None).
        """
        # get all users that need to be synced (enacted < updated or enacted is None)
        pending_slivers = Sliver.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))
        for sliver in pending_slivers:
            if sliver.creator:  
                # update manager context
                self.manager.init_caller(sliver.creator)
                self.manager.save_sliver(sliver)
                sliver.enacted = datetime.now()
                sliver.save()

        # get all slivers that where enacted != null. We can assume these users
        # have previously been synced and need to be checed for deletion.
        slivers = Sliver.objects.filter(enacted__isnull=False)
        sliver_dict = {}
        for sliver in slivers:
            sliver_dict[sliver.instance_id] = sliver

        # delete sliver that don't have a sliver record
        ctx = self.manager.driver.shell.nova_db.ctx 
        instances = self.manager.driver.shell.nova_db.instance_get_all(ctx)
        for instance in instances:
            if instance.id not in sliver_dict:
                # lookup tenant and update context  
                tenant = self.manager.driver.shell.keystone.tenants.findall(id=instance.tenant_id) 
                self.manager.init_admin(tenant=tenant.name)  
                self.manager.driver.destroy_instance(instance.id)
