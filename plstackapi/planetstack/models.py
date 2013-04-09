import os
import datetime
from django.db import models
from plstackapi.openstack.driver import OpenStackDriver

# Create your models here.

class PlCoreBase(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def save(self):
        if not self.id:
            self.created = datetime.date.today()
        self.updated = datetime.datetime.today()
        super(PlCoreBase, self).save()

class Role(PlCoreBase):

    ROLE_CHOICES = (('admin', 'Admin'), ('pi', 'Principle Investigator'), ('user','User'))
    role_id = models.CharField(max_length=256, unique=True)
    role_type = models.CharField(max_length=80, unique=True, choices=ROLE_CHOICES)

    def __unicode__(self):  return u'%s' % (self.role_type)

    def save(self):
        if not self.id:
            self.created = datetime.date.today()
        self.updated = datetime.datetime.today()
        super(Role, self).save()

class Site(PlCoreBase):
    tenant_id = models.CharField(max_length=200, help_text="Keystone tenant id")
    name = models.CharField(max_length=200, help_text="Name for this Site")
    site_url = models.URLField(null=True, blank=True, max_length=512, help_text="Site's Home URL Page")
    enabled = models.BooleanField(default=True, help_text="Status for this Site")
    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    login_base = models.CharField(max_length=50, unique=True, help_text="Prefix for Slices associated with this Site")
    is_public = models.BooleanField(default=True, help_text="Indicates the visibility of this site to other members")
    abbreviated_name = models.CharField(max_length=80)

    def __unicode__(self):  return u'%s' % (self.name)


class User(PlCoreBase):
    user_id = models.CharField(max_length=256, unique=True)
    firstname = models.CharField(help_text="person's given name", max_length=200)
    lastname = models.CharField(help_text="person's surname", max_length=200)
    email = models.EmailField(help_text="e-mail address")
    phone = models.CharField(null=True, blank=True, help_text="phone number contact", max_length=100)
    user_url = models.URLField(null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    site = models.ForeignKey(Site, related_name='users', verbose_name="Site this user will be homed too")

    def __unicode__(self):  return u'%s' % (self.email)

    def save(self, *args, **kwds):
        driver  = OpenStackDriver()
        name = self.email[:self.email.find('@')]
        fields = {'name': name, 'email': self.email, 'password': self.password,
                  'enabled': self.enabled}
        if not self.id:
            user = driver.create_user(**fields) 
        else:
            driver.update_user(self.user_id, **fields)
        super(User, self).save(*args, **kwds)

    def delete(self, *args, **kwds):
        driver = OpenStackDriver()
        driver.delete_user(self.user_id)
        super(User, self).delete(*args, **kwds)

class SitePrivilege(PlCoreBase):

    user = models.ForeignKey('User')
    site = models.ForeignKey('Site', related_name='site_privileges')
    role = models.ForeignKey('Role')

    def __unicode__(self):  return u'%s %s %s' % (self.site, self.user, self.role)

    def save(self, *args, **kwds):
        driver  = OpenStackDriver()
        driver.add_user_role(user_id=user.user_id, 
                             tenant_id=site.tenant_id, 
                             role_name=role.name)
        super(SitePrivilege, self).save(*args, **kwds)

    def delete(self, *args, **kwds):
        driver = OpenStackDriver()
        driver.delete_user_role(user_id=user.user_id,
                                tenant_id=site.tenant_id,
                                role_name=role.name)
        super(SitePrivilege, self).delete(*args, **kwds)
         

class DeploymentNetwork(PlCoreBase):
    name = models.CharField(max_length=200, unique=True, help_text="Name of the Deployment Network")

    def __unicode__(self):  return u'%s' % (self.name)

class SiteDeploymentNetwork(PlCoreBase):
    class Meta:
        unique_together = ['site', 'deploymentNetwork']

    site = models.ForeignKey(Site, related_name='deployment_networks')
    deploymentNetwork = models.ForeignKey(DeploymentNetwork, related_name='sites')
    name = models.CharField(default="Blah", max_length=100)


    def __unicode__(self):  return u'%s::%s' % (self.site, self.deploymentNetwork)


class Slice(PlCoreBase):
    tenant_id = models.CharField(max_length=200, help_text="Keystone tenant id")
    name = models.CharField(help_text="The Name of the Slice", max_length=80)
    enabled = models.BooleanField(default=True, help_text="Status for this Slice")
    SLICE_CHOICES = (('plc', 'PLC'), ('delegated', 'Delegated'), ('controller','Controller'), ('none','None'))
    instantiation = models.CharField(help_text="The instantiation type of the slice", max_length=80, choices=SLICE_CHOICES)
    omf_friendly = models.BooleanField()
    description=models.TextField(blank=True,help_text="High level description of the slice and expected activities", max_length=1024)
    slice_url = models.URLField(blank=True, max_length=512)
    site = models.ForeignKey(Site, related_name='slices', help_text="The Site this Node belongs too")
    network_id = models.CharField(max_length=256, help_text="Quantum network")
    router_id = models.CharField(max_length=256, help_text="Quantum router id")

    def __unicode__(self):  return u'%s' % (self.name)

    def save(self, *args, **kwds):
        # sync keystone tenant
        driver  = OpenStackDriver()

        if not self.id:
            tenant = driver.create_tenant(tenant_name=self.name,
                                          description=self.description,
                                          enabled=self.enabled)
            self.tenant_id = tenant.id
            
            # create a network  
            network = driver.create_network(name=self.name)
            self.network_id = network['id']        
            # create router
            router = driver.create_router(name=self.name)
            self.router_id = router['id']     

        else:
            # update record
            self.driver.update_tenant(self.tenant_id, name=self.name,
                                      description=self.description, enabled=self.enabled)
        super(Slice, self).save(*args, **kwds)

    def delete(self, *args, **kwds):
        # delete keystone tenant
        driver  = OpenStackDriver()
        driver.delete_tenant(self.tenant_id)
        super(Slice, self).delete(*args, **kwds)

class SliceMembership(PlCoreBase):
    user = models.ForeignKey('User')
    slice = models.ForeignKey('Slice')
    role = models.ForeignKey('Role')

    def __unicode__(self):  return u'%s %s %s' % (self.slice, self.user, self.role)

    def save(self, *args, **kwds):
        driver  = OpenStackDriver()
        driver.add_user_role(user_id=user.user_id,
                             tenant_id=slice.tenant_id,
                             role_name=role.name)
        super(SliceMembership, self).save(*args, **kwds)

    def delete(self, *args, **kwds):
        driver = OpenStackDriver()
        driver.delete_user_role(user_id=user.user_id,
                                tenant_id=slice.tenant_id,
                                role_name=role.name)
        super(SliceMembership, self).delete(*args, **kwds)

class SubNet(PlCoreBase):
    subnet_id = models.CharField(max_length=256, unique=True)
    cidr = models.CharField(max_length=20)
    ip_version = models.IntegerField()
    start = models.IPAddressField()
    end = models.IPAddressField()
    slice = models.ForeignKey(Slice )

    def __unicode__(self):  return u'%s' % (self.name)

    def save(self, *args, **kwargs):
        driver  = OpenStackDriver()
        if not self.id:
            subnet = driver.create_subnet(network_name=self.slice.name,
                                          cidr_ip = self.cidr,
                                          ip_version=self.ip_version,
                                          start = self.start,
                                          end = self.end)

            self.subnet_id = subnet.id

        # add subnet as interface to slice router
        driver.add_router_interface(self.slice.router_id, subnet.id)

        super(SubNet, self).save(*args, **kwargs)


    def delete(self, *args, **kwargs):
        # delete quantum network
        driver  = OpenStackDriver()
        driver.delete_subnet(self.subnet_id)
        driver.delete_router_interface(self.slice.router_id, self.subnet.id)
        super(SubNet, self).delete(*args, **kwargs)

class Node(PlCoreBase):
    name = models.CharField(max_length=200, unique=True, help_text="Name of the Node")
    siteDeploymentNetwork = models.ForeignKey(SiteDeploymentNetwork, help_text="The Site and Deployment Network this Node belongs too.")

    def __unicode__(self):  return u'%s' % (self.name)

class Image(PlCoreBase):
    image_id = models.CharField(max_length=256, unique=True)
    name = models.CharField(max_length=256, unique=True)
    disk_format = models.CharField(max_length=256)
    container_format = models.CharField(max_length=256)

    def __unicode__(self):  return u'%s' % (self.name)


class Flavor(PlCoreBase):
    flavor_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=256, unique=True)
    memory_mb = models.IntegerField()
    disk_gb = models.IntegerField()
    vcpus = models.IntegerField()

    def __unicode__(self):  return u'%s' % (self.name)

class Key(PlCoreBase):
    name = models.CharField(max_length=256, unique=True)
    key = models.CharField(max_length=512)
    type = models.CharField(max_length=256)
    blacklisted = models.BooleanField()
    user = models.ForeignKey(User)

    def __unicode__(self):  return u'%s' % (self.name)

    def save(self, *args, **kwds):
        driver  = OpenStackDriver()
        if not self.id:
            keypair = driver.create_keypair(name=self.name, key=self.key)
        super(Key, self).save(*args, **kwds)

    def delete(self, *args, **kwds):
        driver  = OpenStackDriver()
        driver.delete_keypair(self.name)
        super(Key, self).delete(*args, **kwds)



class Sliver(PlCoreBase):
    instance_id = models.CharField(max_length=200, help_text="Nova instance id")    
    name = models.CharField(max_length=200, help_text="Sliver name")
    flavor = models.ForeignKey(Flavor)
    image = models.ForeignKey(Image) 
    key = models.ForeignKey(Key)        
    slice = models.ForeignKey(Slice)
    siteDeploymentNetwork = models.ForeignKey(SiteDeploymentNetwork)
    node = models.ForeignKey(Node)

    def __unicode__(self):  return u'%s::%s' % (self.slice, self.siteDeploymentNetwork)

    def save(self, *args, **kwds):
        driver  = OpenStackDriver()
        instance = driver.spawn_instances(name=self.name,
                                          keyname=self.name,
                                          hostnames=self.node.name,
                                          flavor=self.flavor.name,
                                          image=self.image.name)
        self.instance_id = instance.id
        super(Sliver, self).save(*args, **kwds)

    def delete(self, *args, **kwds):
        driver  = OpenStackDriver()
        driver.destroy_instance(name=self.name, id=self.instance_id)
        super(Sliver, self).delete(*args, **kwds)

