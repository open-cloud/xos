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
    admin_user = models.CharField(max_length=200, null=True, blank=True, help_text="Username of an admin user at this deployment")
    admin_password = models.CharField(max_length=200, null=True, blank=True, help_text="Password of theadmin user at this deployment")
    admin_tenant = models.CharField(max_length=200, null=True, blank=True, help_text="Name of the tenant the admin user belongs to") 
    auth_url = models.CharField(max_length=200, null=True, blank=True, help_text="Auth url for the deployment")
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

    @staticmethod
    def select_by_user(user):
        if user.is_admin:
            qs = DeploymentPrivilege.objects.all()
        else:
            dpriv_ids = [dp.id for dp in DeploymentPrivilege.objects.filter(user=user)]
            qs = DeploymentPrivilege.objects.filter(id__in=dpriv_ids)
        return qs
