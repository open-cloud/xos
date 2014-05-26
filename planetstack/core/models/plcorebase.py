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

class PlCoreBase(models.Model):

    # default values for created and updated are only there to keep evolution
    # from failing.

    created = models.DateTimeField(auto_now_add=True, default=datetime.datetime.now())
    updated = models.DateTimeField(auto_now=True, default=datetime.datetime.now())
    enacted = models.DateTimeField(null=True, default=None)

    class Meta:
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
        pk = self.pk
        model_dict = model_to_dict(self)
        for (k,v) in model_dict.items():
            # things like datetime are not JSON serializable
            model_dict[k] = str(v)

        super(PlCoreBase, self).delete(*args, **kwds)

        # This is a no-op if observer_disabled is set
        notify_observer(model=self, delete=True, pk=pk, model_dict=model_dict)

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



