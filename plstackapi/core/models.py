import os
from django.db import models
from plstackapi.openstack.driver import OpenStackDriver

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plstackapi.planetstack.settings")
# Create your models here.

class PlCoreBase(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Site(PlCoreBase):
    tenant_id = models.CharField(max_length=200, help_text="Keystone tenant id")
    name = models.CharField(max_length=200, unique=True, help_text="Name for this Site")
    site_url = models.URLField(help_text="Site's Home URL Page")
    enabled = models.BooleanField(default=True, help_text="Status for this Site")
    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    login_base = models.CharField(max_length=50, help_text="Prefix for Slices associated with this Site")
    is_public = models.BooleanField(default=True, help_text="Indicates the visibility of this site to other members")
    abbreviated_name = models.CharField(max_length=80)

    def __unicode__(self):  return u'%s' % (self.name)

    def save(self, *args, **kwargs):
        driver  = OpenStackDriver()
        if not self.id:
            tenant = driver.create_tenant(name=self.login_base, 
                                          description=self.name, 
                                          enabled=self.enabled)
            self.tenant_id = tenants.id
        else:
            # update record
            self.driver.update_tenant(self.tenant_id, name=self.login_base,
                                      description=self.name, enabled=self.enabled)
        super(Site, self).save(*args, **kwargs)

    def delete(self, *args, **kwds):
        # delete keystone tenant
        driver  = OpenStackDriver()
        driver.delete_tenant(self.tenant_id)
        super(Site, self).delete(*args, **kwargs)

class Slice(PlCoreBase):
    tenant_id = models.CharField(max_length=200, help_text="Keystone tenant id")
    name = models.CharField(help_text="The Name of the Slice", max_length=80)
    SLICE_CHOICES = (('plc', 'PLC'), ('delegated', 'Delegated'), ('controller','Controller'), ('none','None'))
    instantiation = models.CharField(help_text="The instantiation type of the slice", max_length=80, choices=SLICE_CHOICES)
    omf_friendly = models.BooleanField()
    description=models.TextField(blank=True,help_text="High level description of the slice and expected activities", max_length=1024)
    slice_url = models.URLField(blank=True)
    site = models.ForeignKey(Site, related_name='slices', help_text="The Site this Node belongs too")

    def __unicode__(self):  return u'%s' % (self.name)

    def save(self, *args, **kwds):
        # sync keystone tenant
        driver  = OpenStackDriver()

        tenant_fields = {'name': self.name,
                         'enabled': self.enabled,
                         'description': self.description}
        if not self.id:
            tenant = driver.create_tenant(name=self.name,
                                          description=self.description,
                                          enabled=self.enabled)
            self.tenant_id = tenants.id
        else:
            # update record
            self.driver.update_tenant(self.tenant_id, name=self.name,
                                      description=self.description, enabled=self.enabled)
        super(Slice, self).save(*args, **kwargs)

    def delete(self, *args, **kwds):
        # delete keystone tenant
        driver  = OpenStackDriver()
        driver.delete_tenant(self.tenant_id)
        super(Slice, self).delete(*args, **kwargs)

class DeploymentNetwork(PlCoreBase):
    name = models.CharField(max_length=200, unique=True, help_text="Name of the Deployment Network")

    def __unicode__(self):  return u'%s' % (self.name)

class SiteDeploymentNetwork(PlCoreBase):
    class Meta:
        unique_together = ['site', 'deploymentNetwork']

    site = models.ForeignKey(Site, related_name='deploymentNetworks')
    deploymentNetwork = models.ForeignKey(DeploymentNetwork, related_name='sites')
    name = models.CharField(default="Blah", max_length=100)
    

    def __unicode__(self):  return u'%s::%s' % (self.site, self.deploymentNetwork)


class Sliver(PlCoreBase):
    tenant_id = models.CharField(max_length=200, help_text="Keystone tenant id")
    instance_id = models.CharField(max_length=200, help_text="Nova instance id")    
    name = models.CharField(max_length=200, help_text="Sliver name")
    flavor = models.CharField(max_length=200, help_text="OS Flavor")
    image = models.CharField(max_length=200, help_text="Image Name")    
    slice = models.ForeignKey(Slice, related_name='sliver_slice')
    siteDeploymentNetwork = models.ForeignKey(SiteDeploymentNetwork)
    #node = models.ForeignKey(Node, related_name='node')

    def __unicode__(self):  return u'%s::%s' % (self.slice, self.siteDeploymentNetwork)

    def save(self, *args, **kwds):
        driver  = OpenStackDriver()
        instance = driver.spawn_instances(name=self.name,
                                          keyname=self.name,
                                          hostnames=self.node.name,
                                          flavor=self.flavor,
                                          image=self.image)
        self.instance_id = instance.id
        super(Sliver, self).save(*args, **kwds)

    def delete(self, *args, **kwds):
        driver  = OpenStackDriver()
        driver.destroy_instance(name=self.name, id=self.instance_id)
        super(Sliver, self).delete(*args, **kwds)
        

class Node(PlCoreBase):
    name = models.CharField(max_length=200, unique=True, help_text="Name of the Node")
    siteDeploymentNetwork = models.ForeignKey(SiteDeploymentNetwork, help_text="The Site and Deployment Network this Node belongs too.")

    def __unicode__(self):  return u'%s' % (self.name)

class Network(PlCoreBase):
    slice = models.ForeignKey(Slice, related_name='network_slice')
    name = models.CharField(max_length=200, unique=True)
    quantum_id = models.CharField(max_length=200, unique=True)
    
    def __unicode__(self):  return u'%s' % (self.name)

    def save(self, *args, **kwargs):
        os_shell = OpenStackShell()
        network_fields = {'name': self.name}
        
        if not self.id:
            # check if quantum network record exists
            networks = os_shell.quantum.list_networks(name=self.name)
            if not networks:
                network = os_shell.quantum.create_network(name=self.name,
                                                          admin_state_up=False)
            else:
                network = networks[0]
            self.quantum_id = network.id
        super(Network, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # delete quantum network
        os_shell = OpenStackShell()
        os_shell.quantum.delete_network(self.quantum_id)

        super(Network, self).delete(*args, **kwargs)
        
class SubNet(PlCoreBase):
    network = models.ForeignKey(Network, related_name='network')
    name = models.CharField(max_length=200, unique=True)
    quantum_id = models.CharField(max_length=200, unique=True)
    cidr = models.CharField(max_length=20)
    ip_version = models.IntegerField()
    start = models.IPAddressField()
    end = models.IPAddressField()

    def __unicode__(self):  return u'%s' % (self.name)

    def save(self, *args, **kwargs):
        os_shell = OpenStackShell()
        subnet_fields = {'network_id': self.network.quantum_id,
                         'name' : self.name,
                         'ip_version': self.ip_version,
                         'cidr': self.cidr,
                         'allocation_pools': {'start': self.start,
                                              'end': self.end}
                        }
        if not self.id:
            subnets = os_shell.quantum.list_subnets(name=self.name)
            if not subnets:
                subnet = os_shell.quantum.create_subnet(**subnet_fields)
            else:
                subnet = subnets[0]
            self.quantum_id = subnet.id
        super(SubNet, self).save(*args, **kwargs)


    def delete(self, *args, **kwargs):
        # delete quantum network
        os_shell = OpenStackShell()
        os_shell.quantum.delete_subnet(self.quantum_id)

        super(SubNet, self).delete(*args, **kwargs)
                                                                          
                          
        
