
# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import datetime
import hashlib
import os
import sys
import threading
from collections import defaultdict
from operator import attrgetter, itemgetter

from core.middleware import get_request
from xosbase import XOSBase, PlModelMixIn
from core.models.xosbase import StrippedCharField, XOSCollector
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.db import transaction
from django.db import router
from django.db.models import F, Q
from django.forms.models import model_to_dict
from django.utils import timezone
from timezones.fields import TimeZoneField
from django.contrib.contenttypes.models import ContentType

# The following manual import is needed because we do not
# currently generate the User models.
import security

import redis
from redis import ConnectionError

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
        # user.set_password(password)
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
        parent = super(UserManager, self)
        if hasattr(parent, "get_queryset"):
            return parent.get_queryset().filter(deleted=False)
        else:
            return parent.get_query_set().filter(deleted=False)

    # deprecated in django 1.7 in favor of get_queryset().
    def get_query_set(self):
        return self.get_queryset()


class DeletedUserManager(UserManager):

    def get_queryset(self):
        parent = super(UserManager, self)
        if hasattr(parent, "get_queryset"):
            return parent.get_queryset().filter(deleted=True)
        else:
            return parent.get_query_set().filter(deleted=True)

    # deprecated in django 1.7 in favor of get_queryset()
    def get_query_set(self):
        return self.get_queryset()


class User(AbstractBaseUser, PlModelMixIn):
    plural_name = "Users"

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

    username = StrippedCharField(max_length=255, default="Something")

    firstname = StrippedCharField(
        help_text="person's given name", max_length=200)
    lastname = StrippedCharField(help_text="person's surname", max_length=200)

    phone = StrippedCharField(null=True, blank=True,
                              help_text="phone number contact", max_length=100)
    user_url = models.URLField(null=True, blank=True)
    site = models.ForeignKey('Site', related_name='users',
                             help_text="Site this user will be homed too")
    public_key = models.TextField(
        null=True, blank=True, max_length=1024, help_text="Public key string")

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=True)
    is_readonly = models.BooleanField(default=False)
    is_registering = models.BooleanField(default=False)
    is_appuser = models.BooleanField(default=False)

    login_page = StrippedCharField(
        help_text="send this user to a specific page on login", max_length=200, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    enacted = models.DateTimeField(null=True, default=None)
    policed = models.DateTimeField(null=True, default=None)
    backend_status = StrippedCharField(max_length=1024,
                                       default="Provisioning in progress")
    backend_need_delete = models.BooleanField(default=False)
    backend_need_reap = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    write_protect = models.BooleanField(default=False)
    lazy_blocked = models.BooleanField(default=False)
    no_sync = models.BooleanField(default=False)     # prevent object sync
    no_policy = models.BooleanField(default=False)   # prevent model_policy run

    timezone = TimeZoneField()
    
    leaf_model_name = models.CharField( help_text = "The most specialized model in this chain of inheritance, often defined by a service developer", max_length = 1024, null = False )

    policy_status = models.CharField( default = "0 - Policy in process", max_length = 1024, null = True )

    objects = UserManager()
    deleted_objects = DeletedUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstname', 'lastname']

    PI_FORBIDDEN_FIELDS = ["is_admin", "site", "is_staff"]
    USER_FORBIDDEN_FIELDS = ["is_admin", "is_active",
                             "site", "is_staff", "is_readonly"]

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)
        self._initial = self._dict  # for PlModelMixIn
        self.silent = False

    def isReadOnlyUser(self):
        return self.is_readonly

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

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

    def delete(self, *args, **kwds):
        # so we have something to give the observer
        purge = kwds.get('purge',False)
        if purge:
            del kwds['purge']
        silent = kwds.get('silent',False)
        if silent:
            del kwds['silent']
        try:
            purge = purge or observer_disabled
        except NameError:
            pass

        if (purge):
            super(User, self).delete(*args, **kwds)
        else:
            if (not self.write_protect ):
                self.deleted = True
                self.enacted=None
                self.policed=None
                self.save(update_fields=['enacted','deleted','policed'], silent=silent)

                collector = XOSCollector(using=router.db_for_write(self.__class__, instance=self))
                collector.collect([self])
                with transaction.atomic():
                    for (k, models) in collector.data.items():
                        for model in models:
                            if model.deleted:
                                # in case it's already been deleted, don't delete again
                                continue
                            model.deleted = True
                            model.enacted=None
                            model.policed=None
                            model.save(update_fields=['enacted','deleted','policed'], silent=silent)

    def save(self, *args, **kwargs):
        if not self.leaf_model_name:
            self.leaf_model_name = "User"

        if not self.id:
            self.set_password(self.password)
        if self.is_active and self.is_registering:
            self.send_temporary_password()
            self.is_registering = False

        # let the user specify silence as either a kwarg or an instance varible
        silent = self.silent
        if "silent" in kwargs:
            silent=silent or kwargs.pop("silent")

        caller_kind = "unknown"

        if ('synchronizer' in threading.current_thread().name):
            caller_kind = "synchronizer"

        if "caller_kind" in kwargs:
            caller_kind = kwargs.pop("caller_kind")

        always_update_timestamp = False
        if "always_update_timestamp" in kwargs:
            always_update_timestamp = always_update_timestamp or kwargs.pop("always_update_timestamp")

        # SMBAKER: if an object is trying to delete itself, or if the observer
        # is updating an object's backend_* fields, then let it slip past the
        # composite key check.
        ignore_composite_key_check=False
        if "update_fields" in kwargs:
            ignore_composite_key_check=True
            for field in kwargs["update_fields"]:
                if not (field in ["backend_register", "backend_status", "deleted", "enacted", "updated"]):
                    ignore_composite_key_check=False

        if (caller_kind!="synchronizer") or always_update_timestamp:
            self.updated = timezone.now()

        if not self.username:
            self.username = self.email

        super(User, self).save(*args, **kwargs)

        self.push_redis_event()

        self._initial = self._dict

    def send_temporary_password(self):
        password = User.objects.make_random_password()
        self.set_password(password)
        subject, from_email, to = 'OpenCloud Account Credentials', 'support@opencloud.us', str(
            self.email)
        text_content = 'This is an important message.'
        userUrl = "http://%s/" % get_request().get_host()
        html_content = """<p>Your account has been created on OpenCloud. Please log in <a href=""" + userUrl + """>here</a> to activate your account<br><br>Username: """ + \
            self.email + """<br>Temporary Password: """ + password + \
            """<br>Please change your password once you successully login into the site.</p>"""
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    def apply_profile(self, profile):
        if profile == "regular":
            self.is_appuser = False
            self.is_admin = False

        elif profile == "cp":
            self.is_appuser = True
            self.is_admin = False

    def get_content_type_key(self):
        ct = ContentType.objects.get_for_model(self.__class__)
        return "%s.%s" % (ct.app_label, ct.model)

    @staticmethod
    def get_content_type_from_key(key):
        (app_name, model_name) = key.split(".")
        return ContentType.objects.get_by_natural_key(app_name, model_name)

    @staticmethod
    def get_content_object(content_type, object_id):
        ct = User.get_content_type_from_key(content_type)
        cls = ct.model_class()
        return cls.objects.get(id=object_id)

    ''' This function is hardcoded here because we do not yet
    generate the User class'''
    def can_access(self, ctx):
        return security.user_policy_security_check(self, ctx), "user_policy"

