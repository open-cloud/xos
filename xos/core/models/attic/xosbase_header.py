import datetime
import json
import pytz
import inspect
import sys
import threading
from django.db import models
from django.utils.timezone import now
from django.db.models import *
from django.db import transaction
from django.forms.models import model_to_dict
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from cgi import escape as html_escape
from django.db.models.deletion import Collector
from django.db import router
from django.contrib.contenttypes.models import ContentType

import redis
from redis import ConnectionError

def date_handler(obj):
    if isinstance(obj, pytz.tzfile.DstTzInfo):
        # json can't serialize DstTzInfo
        return str(obj)
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj

class StrippedCharField(models.CharField):
    """ CharField that strips trailing and leading spaces."""
    def clean(self, value, *args, **kwds):
        if value is not None:
            value = value.strip()
        return super(StrippedCharField, self).clean(value, *args, **kwds)


# This manager will be inherited by all subclasses because
# the core model is abstract.
class XOSBaseDeletionManager(models.Manager):
    def get_queryset(self):
        parent=super(XOSBaseDeletionManager, self)
        if hasattr(parent, "get_queryset"):
            return parent.get_queryset().filter(deleted=True)
        else:
            return parent.get_query_set().filter(deleted=True)

    # deprecated in django 1.7 in favor of get_queryset().
    def get_query_set(self):
        return self.get_queryset()

# This manager will be inherited by all subclasses because
# the core model is abstract.
class XOSBaseManager(models.Manager):
    def get_queryset(self):
        parent=super(XOSBaseManager, self)
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

    # This is broken out of XOSBase into a Mixin so the User model can
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

    def get_backend_register(self, k, default=None):
        try:
            return json.loads(self.backend_register).get(k, default)
        except AttributeError:
            return default

    def set_backend_register(self, k, v):
        br = {}
        try:
            br=json.loads(self.backend_register)
        except AttributeError:
            br={}

        br[k] = v
        self.backend_register = json.dumps(br)

    def get_backend_details(self):
        try:
            scratchpad = json.loads(self.backend_register)
        except AttributeError:
            return (None, None, None, None)

        try:
            exponent = scratchpad['exponent']
        except KeyError:
            exponent = None

        try:
            last_success_time = scratchpad['last_success']
            dt = datetime.datetime.fromtimestamp(last_success_time)
            last_success = dt.strftime("%Y-%m-%d %H:%M")
        except KeyError:
            last_success = None

        try:
            failures = scratchpad['failures']
        except KeyError:
            failures=None

        try:
            last_failure_time = scratchpad['last_failure']
            dt = datetime.datetime.fromtimestamp(last_failure_time)
            last_failure = dt.strftime("%Y-%m-%d %H:%M")
        except KeyError:
            last_failure = None

        return (exponent, last_success, last_failure, failures)

    def get_backend_icon(self):
        is_perfect = (self.backend_status is not None) and self.backend_status.startswith("1 -")
        is_good = (self.backend_status is not None) and (self.backend_status.startswith("0 -") or self.backend_status.startswith("1 -"))
        is_provisioning = self.backend_status is None or self.backend_status == "Provisioning in progress" or self.backend_status==""

        # returns (icon_name, tooltip)
        if (self.enacted is not None) and (self.enacted >= self.updated and is_good) or is_perfect:
            return ("success", "successfully enacted")
        else:
            if is_good or is_provisioning:
                return ("clock", "Pending sync, last_status = " + html_escape(self.backend_status, quote=True))
            else:
                return ("error", html_escape(self.backend_status, quote=True))

    def enforce_choices(self, field, choices):
        choices = [x[0] for x in choices]
        for choice in choices:
            if field==choice:
                return
            if (choice==None) and (field==""):
                # allow "" and None to be equivalent
                return
        raise Exception("Field value %s is not in %s" % (field, str(choices)))

    def serialize_for_redis(self):
        """ Serialize the object for posting to redis.

            The API serializes ForeignKey fields by naming them <name>_id
            whereas model_to_dict leaves them with the original name. Modify
            the results of model_to_dict to provide the same fieldnames.
        """

        field_types = {}
        for f in self._meta.fields:
            field_types[f.name] = f.get_internal_type()

        fields = model_to_dict(self)
        for k in fields.keys():
            if field_types.get(k,None) == "ForeignKey":
                new_key_name = "%s_id" % k
                if (k in fields) and (new_key_name not in fields):
                    fields[new_key_name] = fields[k]
                    del fields[k]

        return fields

    def push_redis_event(self):
        # Transmit update via Redis
        changed_fields = []

        if self.pk is not None:
            my_model = type(self)
            try:
                orig = my_model.objects.get(pk=self.pk)

                for f in my_model._meta.fields:
                    oval = getattr(orig, f.name)
                    nval = getattr(self, f.name)
                    if oval != nval:
                        changed_fields.append(f.name)
            except:
                changed_fields.append('__lookup_error')

        try:
            r = redis.Redis("redis")
            # NOTE the redis event has been extended with model properties to facilitate the support of real time notification in the UI
            # keep this monitored for performance reasons and eventually revert it back to fetch model properties via the REST API
            model = self.serialize_for_redis()
            bases = inspect.getmro(self.__class__)
            # bases = [x for x in bases if issubclass(x, XOSBase)]
            class_names = ",".join([x.__name__ for x in bases])
            model['class_names'] = class_names
            payload = json.dumps({'pk': self.pk, 'changed_fields': changed_fields, 'object': model}, default=date_handler)
            r.publish(self.__class__.__name__, payload)
        except ConnectionError:
            # Redis not running.
            pass

# For cascading deletes, we need a Collector that doesn't do fastdelete,
# so we get a full list of models.
class XOSCollector(Collector):
  def can_fast_delete(self, *args, **kwargs):
    return False

class ModelLink:
    def __init__(self,dest,via,into=None):
        self.dest=dest
        self.via=via
        self.into=into

