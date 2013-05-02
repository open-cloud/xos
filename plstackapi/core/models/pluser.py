import os
import datetime
from django.db import models
from plstackapi.core.models import PlCoreBase
from plstackapi.core.models import Site
from plstackapi.openstack.manager import OpenStackManager
from django.contrib.auth.models import User, AbstractBaseUser, UserManager, BaseUserManager

# Create your models here.

class PLUserManager(BaseUserManager):
    def create_user(self, email, firstname, lastname, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=PLUserManager.normalize_email(email),
            firstname=firstname,
            lastname=lastname
        )

        user.set_password(password)
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


class PLUser(AbstractBaseUser):

    class Meta:
        app_label = "core"

    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
        db_index=True,
    )

    user_id = models.CharField(help_text="keystone user id", max_length=200) 
    firstname = models.CharField(help_text="person's given name", max_length=200)
    lastname = models.CharField(help_text="person's surname", max_length=200)

    phone = models.CharField(null=True, blank=True, help_text="phone number contact", max_length=100)
    user_url = models.URLField(null=True, blank=True)
    site = models.ForeignKey(Site, related_name='users', verbose_name="Site this user will be homed too", null=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)

    objects = PLUserManager()

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

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


    def save(self, *args, **kwds):
        if not hasattr(self, 'os_manager'):
            setattr(self, 'os_manager', OpenStackManager())

        self.os_manager.save_user(self)
        self.set_password(self.password)    
        super(PLUser, self).save(*args, **kwds)   

    def delete(self, *args, **kwds):
        if not hasattr(self, 'os_manager'):
            setattr(self, 'os_manager', OpenStackManager())

        self.os_manager.delete_user(self)
        super(PLUser, self).delete(*args, **kwds)    
