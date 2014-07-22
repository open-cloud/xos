import datetime
import os
import sys
from django.db import models
from django.forms.models import model_to_dict
from django.core.urlresolvers import reverse
from django.forms.models import model_to_dict

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
    def get_query_set(self):
        return super(PlCoreBaseDeletionManager, self).get_query_set().filter(deleted=True)

# This manager will be inherited by all subclasses because
# the core model is abstract.
class PlCoreBaseManager(models.Manager):
    def get_query_set(self):
        return super(PlCoreBaseManager, self).get_query_set().filter(deleted=False)

class PlCoreBase(models.Model):
    objects = PlCoreBaseManager()
    deleted_objects = PlCoreBaseDeletionManager()

    # default values for created and updated are only there to keep evolution
    # from failing.
    created = models.DateTimeField(auto_now_add=True, default=datetime.datetime.now())
    updated = models.DateTimeField(auto_now=True, default=datetime.datetime.now())
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
        self.__initial = self._dict

    @property
    def diff(self):
        d1 = self.__initial
        d2 = self._dict
        diffs = [(k, (v, d2[k])) for k, v in d1.items() if v != d2[k]]
        return dict(diffs)

    @property
    def has_changed(self):
        return bool(self.diff)

    @property
    def changed_fields(self):
        return self.diff.keys()

    def get_field_diff(self, field_name):
        return self.diff.get(field_name, None)

    def can_update(self, user):
        if user.is_readonly:
            return False
        if user.is_admin:
            return True
        return False

    def delete(self, *args, **kwds):
        # so we have something to give the observer
        purge = kwds.get('purge',False)
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
            self.save(update_fields=['enacted','deleted'])


    def save(self, *args, **kwargs):
        super(PlCoreBase, self).save(*args, **kwargs)

        # This is a no-op if observer_disabled is set
        notify_observer()

        self.__initial = self._dict

    def save_by_user(self, user, *args, **kwds):
        if self.can_update(user):
            self.save(*args, **kwds)

    def delete_by_user(self, user, *args, **kwds):
        if self.can_update(user):
            self.delete(*args, **kwds)

    @property
    def _dict(self):
        return model_to_dict(self, fields=[field.name for field in
                             self._meta.fields])



