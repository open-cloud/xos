import datetime
import os
import sys
from django.db import models
from django.forms.models import model_to_dict
from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict
from django.utils import timezone
from django.core.exceptions import PermissionDenied
import model_policy
from model_autodeletion import ephemeral_models
from cgi import escape as html_escape

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

class PlModelMixIn(object):
    # Provides useful methods for computing which objects in a model have
    # changed. Make sure to do self._initial = self._dict in the __init__
    # method.

    # Also includes useful utility, like getValidators

    # This is broken out of PlCoreBase into a Mixin so the User model can
    # also make use of it.

    @property
    def _dict(self):
        return model_to_dict(self, fields=[field.name for field in
                             self._meta.fields])

    def fields_differ(self,f1,f2):
        if isinstance(f1,datetime.datetime) and isinstance(f2,datetime.datetime) and (timezone.is_aware(f1) != timezone.is_aware(f2)):
            return True
        else:
            return (f1 != f2)

    @property
    def diff(self):
        d1 = self._initial
        d2 = self._dict
        diffs = [(k, (v, d2[k])) for k, v in d1.items() if self.fields_differ(v,d2[k])]
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

    def get_backend_icon(self):
        is_good = (self.backend_status is not None) and (self.backend_status.startswith("0 -") or self.backend_status.startswith("1 -"))
        is_provisioning = self.backend_status is None or self.backend_status == "Provisioning in progress" or self.backend_status==""

        # returns (icon_name, tooltip)
        if (self.enacted is not None) and self.enacted >= self.updated and is_good:
            return ("success", "successfully enacted")
        else:
            if is_good or is_provisioning:
                return ("clock", "Pending sync, last_status = " + html_escape(self.backend_status, quote=True))
            else:
                return ("error", html_escape(self.backend_status, quote=True))

class PlCoreBase(models.Model, PlModelMixIn):
    objects = PlCoreBaseManager()
    deleted_objects = PlCoreBaseDeletionManager()

    # default values for created and updated are only there to keep evolution
    # from failing.
    created = models.DateTimeField(auto_now_add=True, default=timezone.now)
    updated = models.DateTimeField(auto_now=True, default=timezone.now)
    enacted = models.DateTimeField(null=True, blank=True, default=None)
    policed = models.DateTimeField(null=True, blank=True, default=None)

    # This is a scratchpad used by the Observer
    backend_register = models.CharField(max_length=140,
                                      default="{}", null=True)

    backend_status = models.CharField(max_length=1024,
                                      default="0 - Provisioning in progress")
    deleted = models.BooleanField(default=False)

    class Meta:
        # Changing abstract to False would require the managers of subclasses of
        # PlCoreBase to be customized individually.
        abstract = True
        app_label = "core"

    def __init__(self, *args, **kwargs):
        super(PlCoreBase, self).__init__(*args, **kwargs)
        self._initial = self._dict # for PlModelMixIn
        self.silent = False

    def can_update(self, user):
        return user.can_update_root()

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
        # if not silent:
        #    notify_observer()

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

    @classmethod
    def is_ephemeral(cls):
	return cls in ephemeral_models






