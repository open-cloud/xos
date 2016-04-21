import os
from django.db import models
from django.db.models import Q
from django.contrib.contenttypes import generic
from django.core.exceptions import PermissionDenied
from geoposition.fields import GeopositionField
from core.models import PlCoreBase,PlCoreBaseManager,PlCoreBaseDeletionManager
from core.models import Tag
from core.models.plcorebase import StrippedCharField
from core.acl import AccessControlList
from xos.config import Config

config = Config()

class ControllerLinkDeletionManager(PlCoreBaseDeletionManager):
    def get_queryset(self):
        parent=super(ControllerLinkDeletionManager, self)
        try:
            backend_type = config.observer_backend_type
        except AttributeError:
            backend_type = None

        parent_queryset = parent.get_queryset() if hasattr(parent, "get_queryset") else parent.get_query_set()
        if (backend_type):
            return parent_queryset.filter(Q(controller__backend_type=backend_type))
        else:
            return parent_queryset

    # deprecated in django 1.7 in favor of get_queryset().
    def get_query_set(self):
        return self.get_queryset()


class ControllerDeletionManager(PlCoreBaseDeletionManager):
    def get_queryset(self):
        parent=super(ControllerDeletionManager, self)

        try:
            backend_type = config.observer_backend_type
        except AttributeError:
            backend_type = None

        parent_queryset = parent.get_queryset() if hasattr(parent, "get_queryset") else parent.get_query_set()

        if backend_type:
            return parent_queryset.filter(Q(backend_type=backend_type))
        else:
            return parent_queryset

    # deprecated in django 1.7 in favor of get_queryset().
    def get_query_set(self):
        return self.get_queryset()

class ControllerLinkManager(PlCoreBaseManager):
    def get_queryset(self):
        parent=super(ControllerLinkManager, self)

        try:
            backend_type = config.observer_backend_type
        except AttributeError:
            backend_type = None

        parent_queryset = parent.get_queryset() if hasattr(parent, "get_queryset") else parent.get_query_set()

        if backend_type:
            return parent_queryset.filter(Q(controller__backend_type=backend_type))
        else:
            return parent_queryset

    # deprecated in django 1.7 in favor of get_queryset().
    def get_query_set(self):
        return self.get_queryset()


class ControllerManager(PlCoreBaseManager):
    def get_queryset(self):
        parent=super(ControllerManager, self)

        try:
            backend_type = config.observer_backend_type
        except AttributeError:
            backend_type = None

        parent_queryset = parent.get_queryset() if hasattr(parent, "get_queryset") else parent.get_query_set()

        if backend_type:
            return parent_queryset.filter(Q(backend_type=backend_type))
        else:
            return parent_queryset

    # deprecated in django 1.7 in favor of get_queryset().
    def get_query_set(self):
        return self.get_queryset()

class Site(PlCoreBase):
    """
        A logical grouping of Nodes that are co-located at the same geographic location, which also typically corresponds to the Nodes' location in the physical network.
    """
    name = StrippedCharField(max_length=200, help_text="Name for this Site")
    site_url = models.URLField(null=True, blank=True, max_length=512, help_text="Site's Home URL Page")
    enabled = models.BooleanField(default=True, help_text="Status for this Site")
    hosts_nodes = models.BooleanField(default=True, help_text="Indicates whether or not the site host nodes")
    hosts_users = models.BooleanField(default=True, help_text="Indicates whether or not the site manages user accounts")
    location = GeopositionField()
    longitude = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    login_base = StrippedCharField(max_length=50, unique=True, help_text="Prefix for Slices associated with this Site")
    is_public = models.BooleanField(default=True, help_text="Indicates the visibility of this site to other members")
    abbreviated_name = StrippedCharField(max_length=80)

    #deployments = models.ManyToManyField('Deployment', blank=True, related_name='sites')
    deployments = models.ManyToManyField('Deployment', through='SiteDeployment', blank=True, help_text="Select which sites are allowed to host nodes in this deployment", related_name='sites')
    tags = generic.GenericRelation(Tag)

    def __unicode__(self):  return u'%s' % (self.name)

    def can_update(self, user):
        return user.can_update_site(self, allow=['pi'])

class SiteRole(PlCoreBase):

    ROLE_CHOICES = (('admin','Admin'),('pi','PI'),('tech','Tech'),('billing','Billing'))
    role = StrippedCharField(choices=ROLE_CHOICES, unique=True, max_length=30)

    def __unicode__(self):  return u'%s' % (self.role)

class SitePrivilege(PlCoreBase):

    user = models.ForeignKey('User', related_name='siteprivileges')
    site = models.ForeignKey('Site', related_name='siteprivileges')
    role = models.ForeignKey('SiteRole',related_name='siteprivileges')

    def __unicode__(self):  return u'%s %s %s' % (self.site, self.user, self.role)

    def save(self, *args, **kwds):
        if not self.user.is_active:
            raise PermissionDenied, "Cannot modify role(s) of a disabled user"
        super(SitePrivilege, self).save(*args, **kwds)

    def delete(self, *args, **kwds):
        super(SitePrivilege, self).delete(*args, **kwds)

    def can_update(self, user):
        return user.can_update_site(self, allow=['pi'])

    @staticmethod
    def select_by_user(user):
        if user.is_admin:
            qs = SitePrivilege.objects.all()
        else:
            sp_ids = [sp.id for sp in SitePrivilege.objects.filter(user=user)]
            qs = SitePrivilege.objects.filter(id__in=sp_ids)
        return qs

class Deployment(PlCoreBase):
    #objects = Controllermanager()
    #deleted_objects = DeploymentDeletionManager()
    name = StrippedCharField(max_length=200, unique=True, help_text="Name of the Deployment")
    #admin_user = StrippedCharField(max_length=200, null=True, blank=True, help_text="Username of an admin user at this deployment")
    #admin_password = StrippedCharField(max_length=200, null=True, blank=True, help_text="Password of theadmin user at this deployment")
    #admin_tenant = StrippedCharField(max_length=200, null=True, blank=True, help_text="Name of the tenant the admin user belongs to")
    #auth_url = StrippedCharField(max_length=200, null=True, blank=True, help_text="Auth url for the deployment")
    #backend_type = StrippedCharField(max_length=200, null=True, blank=True, help_text="Type of deployment, e.g. EC2, OpenStack, or OpenStack version")
    #availability_zone = StrippedCharField(max_length=200, null=True, blank=True, help_text="OpenStack availability zone")

    # smbaker: the default of 'allow all' is intended for evolutions of existing
    #    deployments. When new deployments are created via the GUI, they are
    #    given a default of 'allow site <site_of_creator>'
    accessControl = models.TextField(max_length=200, blank=False, null=False, default="allow all",
                                     help_text="Access control list that specifies which sites/users may use nodes in this deployment")
    def __init__(self, *args, **kwargs):
        super(Deployment, self).__init__(*args, **kwargs)
        self.no_sync=True

    def get_acl(self):
        return AccessControlList(self.accessControl)

    def test_acl(self, slice=None, user=None):
        potential_users=[]

        if user:
            potential_users.append(user)

        if slice:
            potential_users.append(slice.creator)
            for priv in slice.sliceprivileges.all():
                if priv.user not in potential_users:
                    potential_users.append(priv.user)

        acl = self.get_acl()
        for user in potential_users:
            if acl.test(user) == "allow":
                return True

        return False

    @staticmethod
    def select_by_acl(user):
        ids = []
        for deployment in Deployment.objects.all():
            acl = deployment.get_acl()
            if acl.test(user) == "allow":
                ids.append(deployment.id)

        return Deployment.objects.filter(id__in=ids)

    def can_update(self, user):
        return user.can_update_deployment(self)
    
    def __unicode__(self):  return u'%s' % (self.name)

class DeploymentRole(PlCoreBase):
    #objects = DeploymentLinkManager()
    #deleted_objects = DeploymentLinkDeletionManager()
    ROLE_CHOICES = (('admin','Admin'),)
    role = StrippedCharField(choices=ROLE_CHOICES, unique=True, max_length=30)

    def __unicode__(self):  return u'%s' % (self.role)

class DeploymentPrivilege(PlCoreBase):
    #objects = DeploymentLinkManager()
    #deleted_objects = DeploymentLinkDeletionManager()

    user = models.ForeignKey('User', related_name='deploymentprivileges')
    deployment = models.ForeignKey('Deployment', related_name='deploymentprivileges')
    role = models.ForeignKey('DeploymentRole',related_name='deploymentprivileges')
    class Meta:
        unique_together = ('user', 'deployment', 'role')

    def __unicode__(self):  return u'%s %s %s' % (self.deployment, self.user, self.role)

    def can_update(self, user):
        return user.can_update_deployment(self)

    @staticmethod
    def select_by_user(user):
        if user.is_admin:
            qs = DeploymentPrivilege.objects.all()
        else:
            dpriv_ids = [dp.id for dp in DeploymentPrivilege.objects.filter(user=user)]
            qs = DeploymentPrivilege.objects.filter(id__in=dpriv_ids)
        return qs

class ControllerRole(PlCoreBase):
    #objects = ControllerLinkManager()
    #deleted_objects = ControllerLinkDeletionManager()

    ROLE_CHOICES = (('admin','Admin'),)
    role = StrippedCharField(choices=ROLE_CHOICES, unique=True, max_length=30)

    def __unicode__(self):  return u'%s' % (self.role)

class Controller(PlCoreBase):

    objects = ControllerManager()
    deleted_objects = ControllerDeletionManager()

    name = StrippedCharField(max_length=200, unique=True, help_text="Name of the Controller")
    backend_type = StrippedCharField(max_length=200, help_text="Type of compute controller, e.g. EC2, OpenStack, or OpenStack version")
    version = StrippedCharField(max_length=200, help_text="Controller version")
    auth_url = StrippedCharField(max_length=200, null=True, blank=True, help_text="Auth url for the compute controller")
    admin_user = StrippedCharField(max_length=200, null=True, blank=True, help_text="Username of an admin user at this controller")
    admin_password = StrippedCharField(max_length=200, null=True, blank=True, help_text="Password of theadmin user at this controller")
    admin_tenant = StrippedCharField(max_length=200, null=True, blank=True, help_text="Name of the tenant the admin user belongs to")
    domain = StrippedCharField(max_length=200, null=True, blank=True, help_text="Name of the domain this controller belongs to")
    rabbit_host = StrippedCharField(max_length=200, null=True, blank=True, help_text="IP address of rabbitmq server at this controller")
    rabbit_user = StrippedCharField(max_length=200, null=True, blank=True, help_text="Username of rabbitmq server at this controller")
    rabbit_password = StrippedCharField(max_length=200, null=True, blank=True, help_text="Password of rabbitmq server at this controller")
    deployment = models.ForeignKey(Deployment,related_name='controllerdeployments')

    def __init__(self, *args, **kwargs):
        super(Controller, self).__init__(*args, **kwargs)
        self.no_sync=True

    def __unicode__(self):  return u'%s %s %s' % (self.name, self.backend_type, self.version)

    @property
    def auth_url_v3(self):
        if self.auth_url and self.auth_url[-1] == '/':
            return '{}/v3/'.format('/'.join(self.auth_url.split('/')[:-2]))
        else:
            return '{}/v3/'.format('/'.join(self.auth_url.split('/')[:-1]))

    @staticmethod
    def select_by_user(user):

        if user.is_admin:
            qs = Controller.objects.all()
        else:
            deployments = [dp.deployment for dp in DeploymentPrivilege.objects.filter(user=user, role__role__in=['Admin', 'admin'])]
            qs = Controller.objects.filter(deployment__in=deployments)
        return qs

class SiteDeployment(PlCoreBase):
    objects = ControllerLinkManager()
    deleted_objects = ControllerLinkDeletionManager()

    site = models.ForeignKey(Site,related_name='sitedeployments')
    deployment = models.ForeignKey(Deployment,related_name='sitedeployments')
    controller = models.ForeignKey(Controller, null=True, blank=True, related_name='sitedeployments')
    availability_zone = StrippedCharField(max_length=200, null=True, blank=True, help_text="OpenStack availability zone")

    class Meta:
        unique_together = ('site', 'deployment', 'controller')

    def __unicode__(self):  return u'%s %s' % (self.deployment, self.site)
    
class ControllerSite(PlCoreBase):
     
    site = models.ForeignKey(Site,related_name='controllersite')
    controller = models.ForeignKey(Controller, null=True, blank=True, related_name='controllersite')
    tenant_id = StrippedCharField(null=True, blank=True, max_length=200, db_index=True, help_text="Keystone tenant id")

    def delete(self, *args, **kwds):
        super(ControllerSite, self).delete(*args, **kwds)

    
    class Meta:
        unique_together = ('site', 'controller') 

class Diag(PlCoreBase):
    name = StrippedCharField(max_length=200, help_text="Name of the synchronizer")
    
    @property
    def enacted(self):
        return None

    @enacted.setter
    def enacted(self, value):
        pass # Ignore sets, Diag objects are always pending.
