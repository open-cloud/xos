import os
import datetime
import sys
import hashlib
from collections import defaultdict
from django.forms.models import model_to_dict
from django.db import models
from django.db.models import F, Q
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.mail import EmailMultiAlternatives
from django.core.exceptions import PermissionDenied
from core.models import PlCoreBase,Site, DashboardView, PlModelMixIn
from core.models.plcorebase import StrippedCharField
from timezones.fields import TimeZoneField
from operator import itemgetter, attrgetter
from core.middleware import get_request
import model_policy

# ------ from plcorebase.py ------
try:
    # This is a no-op if observer_disabled is set to 1 in the config file
    from observer import *
except:
    print >> sys.stderr, "import of observer failed! printing traceback and disabling observer:"
    import traceback
    traceback.print_exc()

    # guard against something failing
    def notify_observer(*args, **kwargs):
        pass
# ------ ------

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, firstname, lastname, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=UserManager.normalize_email(email),
            firstname=firstname,
            lastname=lastname,
            password=password
        )
        #user.set_password(password)
        user.is_admin = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, firstname, lastname, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(email,
            password=password,
            firstname=firstname,
            lastname=lastname
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

    def get_queryset(self):
        parent=super(UserManager, self)
        if hasattr(parent, "get_queryset"):
            return parent.get_queryset().filter(deleted=False)
        else:
            return parent.get_query_set().filter(deleted=False)

    # deprecated in django 1.7 in favor of get_queryset().
    def get_query_set(self):
        return self.get_queryset()

class DeletedUserManager(UserManager):
    def get_queryset(self):
        return super(UserManager, self).get_query_set().filter(deleted=True)

    # deprecated in django 1.7 in favor of get_queryset()
    def get_query_set(self):
        return self.get_queryset()

class User(AbstractBaseUser, PlModelMixIn):
    @property
    def remote_password(self):
        return hashlib.md5(self.password).hexdigest()[:12]

    class Meta:
        app_label = "core"

    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
        db_index=True,
    )

    username = StrippedCharField(max_length=255, default="Something" )

    firstname = StrippedCharField(help_text="person's given name", max_length=200)
    lastname = StrippedCharField(help_text="person's surname", max_length=200)

    phone = StrippedCharField(null=True, blank=True, help_text="phone number contact", max_length=100)
    user_url = models.URLField(null=True, blank=True)
    site = models.ForeignKey(Site, related_name='users', help_text="Site this user will be homed too")
    public_key = models.TextField(null=True, blank=True, max_length=1024, help_text="Public key string")

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)
    is_readonly = models.BooleanField(default=False)
    is_registering = models.BooleanField(default=False)
    is_appuser = models.BooleanField(default=False)

    login_page = StrippedCharField(help_text="send this user to a specific page on login", max_length=200, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    enacted = models.DateTimeField(null=True, default=None)
    policed = models.DateTimeField(null=True, default=None)
    backend_status = StrippedCharField(max_length=1024,
                                      default="Provisioning in progress")
    deleted = models.BooleanField(default=False)
    write_protect = models.BooleanField(default=False)

    timezone = TimeZoneField()

    dashboards = models.ManyToManyField('DashboardView', through='UserDashboardView', blank=True)

    objects = UserManager()
    deleted_objects = DeletedUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstname', 'lastname']

    PI_FORBIDDEN_FIELDS = ["is_admin", "site", "is_staff"]
    USER_FORBIDDEN_FIELDS = ["is_admin", "is_active", "site", "is_staff", "is_readonly"]

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self._initial = self._dict # for PlModelMixIn

    def isReadOnlyUser(self):
        return self.is_readonly

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def delete(self, *args, **kwds):
        # so we have something to give the observer
        purge = kwds.get('purge',False)
        if purge:
            del kwds['purge']
        try:
            purge = purge or observer_disabled
        except NameError:
            pass
            
        if (purge):
            super(User, self).delete(*args, **kwds)
        else:
            if (not self.write_protect):
                    self.deleted = True
                    self.enacted=None
                    self.save(update_fields=['enacted','deleted'])

    @property
    def keyname(self):
        return self.email[:self.email.find('@')]

    def __unicode__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    def is_superuser(self):
        return False

    def get_dashboards(self):
        DEFAULT_DASHBOARDS=["Tenant"]

        dashboards = sorted(list(self.userdashboardviews.all()), key=attrgetter('order'))
        dashboards = [x.dashboardView for x in dashboards]

        if (not dashboards) and (not self.is_appuser):
            for dashboardName in DEFAULT_DASHBOARDS:
                dbv = DashboardView.objects.filter(name=dashboardName)
                if dbv:
                    dashboards.append(dbv[0])

        return dashboards

#    def get_roles(self):
#        from core.models.site import SitePrivilege
#        from core.models.slice import SliceMembership
#
#        site_privileges = SitePrivilege.objects.filter(user=self)
#        slice_memberships = SliceMembership.objects.filter(user=self)
#        roles = defaultdict(list)
#        for site_privilege in site_privileges:
#            roles[site_privilege.role.role_type].append(site_privilege.site.login_base)
#        for slice_membership in slice_memberships:
#            roles[slice_membership.role.role_type].append(slice_membership.slice.name)
#        return roles   

    def save(self, *args, **kwds):
        if not self.id:
            self.set_password(self.password)
        if self.is_active and self.is_registering:
            self.send_temporary_password()
            self.is_registering=False

        self.username = self.email
        super(User, self).save(*args, **kwds)

        self._initial = self._dict

    def send_temporary_password(self):
        password = User.objects.make_random_password()
        self.set_password(password)
        subject, from_email, to = 'OpenCloud Account Credentials', 'support@opencloud.us', str(self.email)
        text_content = 'This is an important message.'
        userUrl="http://%s/" % get_request().get_host()
        html_content = """<p>Your account has been created on OpenCloud. Please log in <a href="""+userUrl+""">here</a> to activate your account<br><br>Username: """+self.email+"""<br>Temporary Password: """+password+"""<br>Please change your password once you successully login into the site.</p>"""
        msg = EmailMultiAlternatives(subject,text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    def can_update(self, user):
        from core.models import SitePrivilege
        _cant_update_fieldName = None
        if user.can_update_root():
            return True

        # site pis can update
        site_privs = SitePrivilege.objects.filter(user=user, site=self.site)
        for site_priv in site_privs:
            if site_priv.role.role == 'admin':
                return True 
            if site_priv.role.role == 'pi':
                for fieldName in self.diff.keys():
                    if fieldName in self.PI_FORBIDDEN_FIELDS:
                        _cant_update_fieldName = fieldName
                        return False
                return True
        if (user.id == self.id):
            for fieldName in self.diff.keys():
                if fieldName in self.USER_FORBIDDEN_FIELDS:
                    _cant_update_fieldName = fieldName
                    return False
            return True

        return False

    def can_update_root(self):
        """
        Return True if user has root (global) write access. 
        """
        if self.is_readonly:
            return False
        if self.is_admin:
            return True

        return False 

    def can_update_deployment(self, deployment):
        from core.models.site import DeploymentPrivilege
        if self.can_update_root():
            return True    
                          
        if DeploymentPrivilege.objects.filter(
            deployment=deployment,
            user=self,
            role__role__in=['admin', 'Admin']):
            return True
        return False    

    def can_update_site(self, site, allow=[]):
        from core.models.site import SitePrivilege
        if self.can_update_root():
            return True
        if SitePrivilege.objects.filter(
            site=site, user=self, role__role__in=['admin', 'Admin']+allow):
            return True
        return False
    
    def can_update_slice(self, slice):
        from core.models.slice import SlicePrivilege
        if self.can_update_root():
            return True
        if self == slice.creator:
            return True
        if self.can_update_site(slice.site, allow=['pi']):
            return True
                     
        if SlicePrivilege.objects.filter(
            slice=slice, user=self, role__role__in=['admin', 'Admin']):
            return True
        return False

    def can_update_service(self, service, allow=[]):
        from core.models.service import ServicePrivilege
        if self.can_update_root():
            return True
        if ServicePrivilege.objects.filter(
            service=service, user=self, role__role__in=['admin', 'Admin']+allow):
            return True
        return False

    def can_update_tenant_root(self, tenant_root, allow=[]):
        from core.models.service import TenantRoot, TenantRootPrivilege
        if self.can_update_root():
            return True
        if TenantRootPrivilege.objects.filter(
            tenant_root=tenant_root, user=self, role__role__in=['admin', 'Admin']+allow):
            return True
        return False

    def can_update_tenant_root_privilege(self, tenant_root_privilege, allow=[]):
        return self.can_update_tenant_root(tenant_root_privilege.tenant_root, allow)

    def get_readable_objects(self, filter=None):
       """ Returns a list of objects that the user is allowed to read. """
       from core.models import Deployment, Network, Site, Slice, SliceTag, Sliver, Tag, User
       models = [Deployment, Network, Site, Slice, SliceTag, Sliver, Tag, User]
       readable_objects = []
       for model in models:
           readable_objects.extend(model.select_by_user(self))
       return readable_objects      

    @staticmethod
    def select_by_user(user):
        if user.is_admin:
            qs = User.objects.all()
        else:
            # can see all users at any site where this user has pi role
            from core.models.site import SitePrivilege
            site_privs = SitePrivilege.objects.filter(user=user)
            sites = [sp.site for sp in site_privs if sp.role.role in ['Admin', 'admin', 'pi']]
            # get site privs of users at these sites
            site_privs = SitePrivilege.objects.filter(site__in=sites)
            user_ids = [sp.user.id for sp in site_privs] + [user.id]
            qs = User.objects.filter(Q(site__in=sites) | Q(id__in=user_ids))
        return qs

    def save_by_user(self, user, *args, **kwds):
        if not self.can_update(user):
            if getattr(self, "_cant_update_fieldName", None) is not None:
                raise PermissionDenied("You do not have permission to update field %s on object %s" % (self._cant_update_fieldName, self.__class__.__name__))
            else:
                raise PermissionDenied("You do not have permission to update %s objects" % self.__class__.__name__)

        self.save(*args, **kwds)

    def delete_by_user(self, user, *args, **kwds):
        if not self.can_update(user):
            raise PermissionDenied("You do not have permission to delete %s objects" % self.__class__.__name__)
        self.delete(*args, **kwds)

    def apply_profile(self, profile):
        if profile=="regular":
            self.is_appuser = False
            self.is_admin = False

        elif profile=="cp":
            self.is_appuser = True
            self.is_admin = False
            for db in self.userdashboardviews.all():
                db.delete()

class UserDashboardView(PlCoreBase):
     user = models.ForeignKey(User, related_name='userdashboardviews')
     dashboardView = models.ForeignKey(DashboardView, related_name='userdashboardviews')
     order = models.IntegerField(default=0)
