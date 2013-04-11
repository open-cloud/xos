import os
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
    slice = models.ForeignKey(Slice, related_name='slice_subnet')

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

        super(Subnet, self).save(*args, **kwargs)


    def delete(self, *args, **kwargs):
        # delete quantum network
        driver  = OpenStackDriver()
        driver.delete_subnet(self.subnet_id)
        driver.delete_router_interface(self.slice.router_id, self.subnet.id)
        super(Subnet, self).delete(*args, **kwargs)
