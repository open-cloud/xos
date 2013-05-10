import os
import datetime
from collections import defaultdict
from django.db import models
from core.models import PlCoreBase
from core.models import Site
from core.models import Key
from openstack.manager import OpenStackManager
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

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


class User(AbstractBaseUser):

    class Meta:
        app_label = "core"

    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
        db_index=True,
    )

    kuser_id = models.CharField(null=True, blank=True, help_text="keystone user id", max_length=200) 
    firstname = models.CharField(help_text="person's given name", max_length=200)
    lastname = models.CharField(help_text="person's surname", max_length=200)

    phone = models.CharField(null=True, blank=True, help_text="phone number contact", max_length=100)
    user_url = models.URLField(null=True, blank=True)
    site = models.ForeignKey(Site, related_name='users', verbose_name="Site this user will be homed too", null=True)
    key = models.ForeignKey(Key, related_name='user', null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstname', 'lastname']

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

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

    def get_roles(self):
        from plstackapi.core.models.site import SitePrivilege
        from plstackapi.core.models.slice import SliceMembership

        site_privileges = SitePrivilege.objects.filter(user=self)
        slice_memberships = SliceMembership.objects.filter(user=self)
        roles = defaultdict(list)
        for site_privilege in site_privileges:
            roles[site_privilege.role.role_type].append(site_privilege.site.login_base)
        for slice_membership in slice_memberships:
            roles[slice_membership.role.role_type].append(slice_membership.slice.name)
        return roles   

    def save(self, *args, **kwds):
        if not hasattr(self, 'os_manager'):
            setattr(self, 'os_manager', OpenStackManager())
            self.os_manager.save_user(self)

        if not self.id:
            self.set_password(self.password)    
        super(User, self).save(*args, **kwds)   

    def delete(self, *args, **kwds):
        if not hasattr(self, 'os_manager'):
            setattr(self, 'os_manager', OpenStackManager())
            self.os_manager.delete_user(self)

        super(User, self).delete(*args, **kwds)    
