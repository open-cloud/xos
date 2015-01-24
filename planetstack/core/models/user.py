import os
import datetime
import sys
import hashlib
from collections import defaultdict
from django.forms.models import model_to_dict
from django.db import models
from django.db.models import F, Q
from core.models import PlCoreBase,Site, DashboardView, DiffModelMixIn
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from timezones.fields import TimeZoneField
from operator import itemgetter, attrgetter
from django.core.mail import EmailMultiAlternatives
from core.middleware import get_request
import model_policy
from django.core.exceptions import PermissionDenied

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

class User(AbstractBaseUser): #, DiffModelMixIn):

    # ---- copy stuff from DiffModelMixin ----

    @property
    def _dict(self):
        return model_to_dict(self, fields=[field.name for field in
                             self._meta.fields])

    @property
    def diff(self):
        d1 = self._initial
        d2 = self._dict
        diffs = [(k, (v, d2[k])) for k, v in d1.items() if v != d2[k]]
        return dict(diffs)

    @property
    def has_changed(self):
        return bool(self.diff)

    @property
    def changed_fields(self):
        return self.diff.keys()

    def has_field_changed(self, field_name):
        return field_name in self.diff.keys()

    def get_field_diff(self, field_name):
        return self.diff.get(field_name, None)

    #classmethod
    def getValidators(cls):
        """ primarily for REST API, return a dictionary of field names mapped
            to lists of the type of validations that need to be applied to
            those fields.
        """
        validators = {}
        for field in cls._meta.fields:
            l = []
            if field.blank==False:
                l.append("notBlank")
            if field.__class__.__name__=="URLField":
                l.append("url")
            validators[field.name] = l
        return validators
    # ---- end copy stuff from DiffModelMixin ----

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

    username = models.CharField(max_length=255, default="Something" )

    firstname = models.CharField(help_text="person's given name", max_length=200)
    lastname = models.CharField(help_text="person's surname", max_length=200)

    phone = models.CharField(null=True, blank=True, help_text="phone number contact", max_length=100)
    user_url = models.URLField(null=True, blank=True)
    site = models.ForeignKey(Site, related_name='users', help_text="Site this user will be homed too", null=True)
    public_key = models.TextField(null=True, blank=True, max_length=1024, help_text="Public key string")

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_readonly = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    enacted = models.DateTimeField(null=True, default=None)
    policed = models.DateTimeField(null=True, default=None)
    backend_status = models.CharField(max_length=140,
                                      default="Provisioning in progress")
    deleted = models.BooleanField(default=False)

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
        self._initial = self._dict # for DiffModelMixIn

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

        if not dashboards:
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
        if self.is_active:
            if self.password=="!":
                self.send_temporary_password()

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
        if user.is_readonly:
            return False
        if user.is_admin:
            return True
        # site pis can update
        site_privs = SitePrivilege.objects.filter(user=user, site=self.site)
        for site_priv in site_privs:
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

    @staticmethod
    def select_by_user(user):
        if user.is_admin:
            qs = User.objects.all()
        else:
            # can see all users at any site where this user has pi role
            from core.models.site import SitePrivilege
            site_privs = SitePrivilege.objects.filter(user=user)
            sites = [sp.site for sp in site_privs if sp.role.role == 'pi']
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

class UserDashboardView(PlCoreBase):
     user = models.ForeignKey(User, related_name='userdashboardviews')
     dashboardView = models.ForeignKey(DashboardView, related_name='userdashboardviews')
     order = models.IntegerField(default=0)
