import os
from django.db import models
from core.models import PlCoreBase
from django.contrib.contenttypes import generic

# Create your models here.

class ManyToManyField_NoSyncdb(models.ManyToManyField):
    def __init__(self, *args, **kwargs):
        super(ManyToManyField_NoSyncdb, self).__init__(*args, **kwargs)
        self.creates_table = False

class Deployment(PlCoreBase):
    name = models.CharField(max_length=200, unique=True, help_text="Name of the Deployment")
#    sites = ManyToManyField_NoSyncdb('Site', through=Site.deployments.through, blank=True)

    def __unicode__(self):  return u'%s' % (self.name)

    
class DeploymentRole(PlCoreBase):

    ROLE_CHOICES = (('admin','Admin'),)
    role = models.CharField(choices=ROLE_CHOICES, unique=True, max_length=30)

    def __unicode__(self):  return u'%s' % (self.role)

class DeploymentPrivilege(PlCoreBase):

    user = models.ForeignKey('User', related_name='deployment_privileges')
    deployment = models.ForeignKey('Deployment', related_name='deployment_privileges')
    role = models.ForeignKey('DeploymentRole')

    def __unicode__(self):  return u'%s %s %s' % (self.deployment, self.user, self.role)


    def can_update(self, user):
        if user.is_readonly:
            return False
        if user.is_admin:
            return True
        dprivs = DeploymentPrivilege.objects.filter(user=user)
        for dpriv in dprivs:
            if dpriv.role.role_type == 'admin':
                return True
        return False

    def save_by_user(self, user, *args, **kwds):
        if self.can_update(user):
            super(DeploymentPrivilege, self).save(*args, **kwds)

    @staticmethod
    def select_by_user(user):
        if user.is_admin:
            qs = DeploymentPrivilege.objects.all()
        else:
            dpriv_ids = [dp.id for dp in DeploymentPrivilege.objects.filter(user=user)]
            qs = DeploymentPrivilege.objects.filter(id__in=dpriv_ids)
        return qs
