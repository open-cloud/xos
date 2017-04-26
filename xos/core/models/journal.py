from __future__ import absolute_import

from django.db import models
from django.utils import timezone

from xos.config import Config
from xos.exceptions import *
from operator import attrgetter
import json

class JournalEntry(models.Model):
    objClassName = models.CharField(max_length=64)
    objId = models.CharField(max_length=64, null=True, blank=True)  # null=True, for objects journaled before save
    objUnicode = models.CharField(max_length=1024)
    operation = models.CharField(max_length=64)
    msg = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __unicode__(self): return u'%s' % (self.name)

    def can_update(self, user):
        return True


def journal_object(o, operation, msg=None, timestamp=None):
    # do not journal unless it has been explicitly enabled
    if not getattr(Config(), "debug_enable_journal", None):
        return

    # ignore objects that generate too much noise
    if o.__class__.__name__ in ["Diag"]:
        return

    if not timestamp:
        timestamp = timezone.now()

    j = JournalEntry(objClassName = o.__class__.__name__,
                     objId = o.id,
                     objUnicode = str(o),
                     operation = operation,
                     msg= msg)
    j.save()



