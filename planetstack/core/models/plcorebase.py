import os
import sys
from django.db import models
from django.forms.models import model_to_dict
from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict
from django.utils import timezone
from django.core.exceptions import PermissionDenied
import model_policy

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

# This manager will be inherited by all subclasses because
# the core model is abstract.
class PlCoreBaseDeletionManager(models.Manager):
    def get_queryset(self):
        parent=super(PlCoreBaseDeletionManager, self)
        if hasattr(parent, "get_queryset"):
            return parent.get_queryset().filter(deleted=True)
        else:
            return parent.get_query_set().filter(deleted=True)

    # deprecated in django 1.7 in favor of get_queryset().
    def get_query_set(self):
        return self.get_queryset()

# This manager will be inherited by all subclasses because
# the core model is abstract.
class PlCoreBaseManager(models.Manager):
    def get_queryset(self):
        parent=super(PlCoreBaseManager, self)
        if hasattr(parent, "get_queryset"):
            return parent.get_queryset().filter(deleted=False)
        else:
            return parent.get_query_set().filter(deleted=False)

    # deprecated in django 1.7 in favor of get_queryset().
    def get_query_set(self):
        return self.get_queryset()

class DiffModelMixIn:
    # Provides useful methods for computing which objects in a model have
    # changed. Make sure to do self._initial = self._dict in the __init__
    # method.

    # This is broken out of PlCoreBase into a Mixin so the User model can
    # also make use of it.

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

class PlCoreBase(models.Model, DiffModelMixIn):
    objects = PlCoreBaseManager()
    deleted_objects = PlCoreBaseDeletionManager()

    # default values for created and updated are only there to keep evolution
    # from failing.
    created = models.DateTimeField(auto_now_add=True, default=timezone.now)
    updated = models.DateTimeField(auto_now=True, default=timezone.now)
    enacted = models.DateTimeField(null=True, default=None)
    backend_status = models.CharField(max_length=140,
                                      default="Provisioning in progress")
    deleted = models.BooleanField(default=False)

    class Meta:
        # Changing abstract to False would require the managers of subclasses of
        # PlCoreBase to be customized individually.
        abstract = True
        app_label = "core"

    def __init__(self, *args, **kwargs):
        super(PlCoreBase, self).__init__(*args, **kwargs)
        self._initial = self._dict # for DiffModelMixIn
        self.silent = False

    def can_update(self, user):
        if user.is_readonly:
            return False
        if user.is_admin:
            return True

        return False

    def delete(self, *args, **kwds):
        # so we have something to give the observer
        purge = kwds.get('purge',False)
        silent = kwds.get('silent',False)
        try:
            purge = purge or observer_disabled
        except NameError:
            pass

        if (purge):
            del kwds['purge']
            super(PlCoreBase, self).delete(*args, **kwds)
        else:
            self.deleted = True
            self.enacted=None
            self.save(update_fields=['enacted','deleted'], silent=silent)

    def save(self, *args, **kwargs):
        # let the user specify silence as either a kwarg or an instance varible
        silent = self.silent
        if "silent" in kwargs:
            silent=silent or kwargs.pop("silent")

        super(PlCoreBase, self).save(*args, **kwargs)

        # This is a no-op if observer_disabled is set
        if not silent:
            notify_observer()

        self._initial = self._dict

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

    @classmethod
    def select_by_user(cls, user):
        # This should be overridden by descendant classes that want to perform
        # filtering of visible objects by user.
        return cls.objects.all()




