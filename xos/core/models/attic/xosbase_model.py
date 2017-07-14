objects = XOSBaseManager()
deleted_objects = XOSBaseDeletionManager()

class Meta:
    # Changing abstract to False would require the managers of subclasses of
    # XOSBase to be customized individually.
    abstract = True
    app_label = "core"

def __init__(self, *args, **kwargs):
    super(XOSBase, self).__init__(*args, **kwargs)
    self._initial = self._dict # for PlModelMixIn
    self.silent = False

def get_controller(self):
    return self.controller

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
        super(XOSBase, self).delete(*args, **kwds)
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

def verify_live_keys(self, update_fields):
    """ Check the fields to be updated, if they contain foreign keys, that the foreign keys only point
        to live objects in the database.

        This is to catch races between model policies where an object is being deleted while a model policy is
        still operating on it.
    """

    if getattr(self, "deleted", False):
        # If this model is already deleted, then no need to check anything. We only need to check for live
        # models that point to dead models. If a dead model points to other dead models, then we could
        # be updating something else in the dead model (backend_status, etc)
        return

    for field in self._meta.fields:
        try:
            f = getattr(self, field.name)
        except Exception, e:
            # Exception django.db.models.fields.related.RelatedObjectDoesNotExist
            # is thrown by django when you're creating an object that has a base and the base doesn't exist yet
            continue

        if f is None:
            # If field hold a null value, we don't care
            continue

        ftype = field.get_internal_type()
        if (ftype != "ForeignKey"):
            # If field isn't a foreign key, we don't care
            continue

        if (update_fields) and (field.name not in update_fields):
            # If update_fields is nonempty, and field is not to be updated, we don't care.
            continue

        if getattr(f, "deleted", False):
            raise Exception("Attempt to save object with deleted foreign key reference")

def save(self, *args, **kwargs):

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

    with transaction.atomic():
        self.verify_live_keys(update_fields = kwargs.get("update_fields"))
        super(XOSBase, self).save(*args, **kwargs)

    self.push_redis_event()

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

def tologdict(self):
    try:
        d = {'model_name':self.__class__.__name__, 'pk': self.pk}
    except:
        d = {}

    return d

# for the old django admin UI
def __unicode__(self):
    if hasattr(self, "name") and self.name:
        return u'%s' % self.name
    elif hasattr(self, "id") and self.id:
        if hasattr(self, "leaf_model_name") and self.leaf_model_name:
            return u'%s-%s' % (self.leaf_model_name, self.id)
        else:
            return u'%s-%s' % (self.__class__.__name__, self.id)
    else:
        return u'%s-unsaved' % self.__class__.__name__

def get_content_type_key(self):
    ct = ContentType.objects.get_for_model(self.__class__)
    return "%s.%s" % (ct.app_label, ct.model)

@staticmethod
def get_content_type_from_key(key):
    (app_name, model_name) = key.split(".")
    return ContentType.objects.get_by_natural_key(app_name, model_name)

@staticmethod
def get_content_object(content_type, object_id):
    ct = XOSBase.get_content_type_from_key(content_type)
    cls = ct.model_class()
    return cls.objects.get(id=object_id)

