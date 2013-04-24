import os
import commands    
from django.db import models
from plstackapi.core.models import PlCoreBase
from plstackapi.core.models import Slice
from plstackapi.openstack.driver import OpenStackDriver

# Create your models here.

class Subnet(PlCoreBase):
    subnet_id = models.CharField(max_length=256, unique=True)
    cidr = models.CharField(max_length=20)
    ip_version = models.IntegerField()
    start = models.IPAddressField()
    end = models.IPAddressField()
    slice = models.ForeignKey(Slice, related_name='subnet')

    def __unicode__(self):  return u'%s' % (self.slice.name)

    def save(self, *args, **kwds):

        driver = OpenStackDriver()
        if not self.subnet_id:
            quantum_subnet = driver.create_subnet(name= self.slice.name,
                                          network_id=self.slice.network_id,
                                          cidr_ip = self.cidr,
                                          ip_version=self.ip_version,
                                          start = self.start,
                                          end = self.end)
            self.subnet_id = quantum_subnet['id']
            # add subnet as interface to slice's router
            driver.add_router_interface(self.slice.router_id, self.subnet_id)
            #add_route = 'route add -net %s dev br-ex gw 10.100.0.5' % self.cidr
            #commands.getstatusoutput(add_route)

        super(Subnet, self).save(*args, **kwds)

    def delete(self, *args, **kwds):
        driver = OpenStackDriver()
        if self.subnet_id:
            driver.delete_router_interface(self.slice.router_id, self.subnet_id) 
            driver.delete_subnet(self.subnet_id)
            #del_route = 'route del -net %s' % self.cidr 
            #commands.getstatusoutput(del_route)
        super(Subnet, self).delete(*args, **kwds)
