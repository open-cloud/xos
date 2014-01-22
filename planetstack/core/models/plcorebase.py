import os
from django.db import models
from django.forms.models import model_to_dict
from django.core.urlresolvers import reverse
# This is a no-op if observer_disabled is set to 1 in the config file
from observer import *

class PlCoreBase(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
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

    def delete(self, *args, **kwds):
        super(PlCoreBase, self).delete(*args, **kwds)

        # This is a no-op if observer_disabled is set
        notify_observer(model=self, delete=True, pk=self.pk)

    def save(self, *args, **kwargs):
        super(PlCoreBase, self).save(*args, **kwargs)
        
        # This is a no-op if observer_disabled is set
        notify_observer()

        self.__initial = self._dict

    @property
    def _dict(self):
        return model_to_dict(self, fields=[field.name for field in
                             self._meta.fields])



