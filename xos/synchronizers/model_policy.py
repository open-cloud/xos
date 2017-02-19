from core.models import *
from datetime import datetime
from django.db import reset_queries
from django.db.models import F, Q
from django.db.models.signals import post_save
from django.db.transaction import atomic
from django.dispatch import receiver
from django.utils import timezone
from django.db import models as django_models
from generate.dependency_walker import *
from xos.logger import Logger, logging

import pdb
import time
import traceback

modelPolicyEnabled = True
bad_instances=[]

model_policies = {}

logger = Logger(level=logging.DEBUG)

def EnableModelPolicy(x):
    global modelPolicyEnabled
    modelPolicyEnabled = x

def update_wp(d, o):
    try:
        save_fields = []
        if (d.write_protect != o.write_protect):
            d.write_protect = o.write_protect
            save_fields.append('write_protect')
        if (save_fields):
            d.save(update_fields=save_fields)
    except AttributeError,e:
        raise e

def update_dep(d, o):
    try:
        print 'Trying to update %s'%d
        save_fields = []
        if (d.updated < o.updated):
            save_fields = ['updated']

        if (save_fields):
            d.save(update_fields=save_fields)
    except AttributeError,e:
        logger.log_exc("AttributeError in update_dep")
        raise e
    except Exception,e:
        logger.log_exc("Exception in update_dep")

def delete_if_inactive(d, o):
    try:
        d.delete()
        print "Deleted %s (%s)"%(d,d.__class__.__name__)
    except:
        pass
    return

def load_model_policies(policies_dir=None):
    global model_policies

    if policies_dir is None:
            policies_dir = Config().observer_model_policies_dir

    for fn in os.listdir(policies_dir):
            pathname = os.path.join(policies_dir,fn)
            if os.path.isfile(pathname) and fn.startswith("model_policy_") and fn.endswith(".py") and (fn!="__init__.py"):
                model_policies[fn[:-3]] = imp.load_source(fn[:-3],pathname)

    logger.debug("Loaded model polices %s from %s" % (",".join(model_policies.keys()), policies_dir))

#@atomic
def execute_model_policy(instance, deleted):
    # Automatic dirtying
    if (instance in bad_instances):
        return

    # These are the models whose children get deleted when they are
    delete_policy_models = ['Slice','Instance','Network']
    sender_name = instance.__class__.__name__
    policy_name = 'model_policy_%s'%sender_name
    noargs = False

    if (not deleted):
        walk_inv_deps(update_dep, instance)
        walk_deps(update_wp, instance)
    elif (sender_name in delete_policy_models):
        walk_inv_deps(delete_if_inactive, instance)

    try:
        policy_handler = model_policies.get(policy_name, None) # getattr(model_policies, policy_name, None)
        logger.debug("MODEL POLICY: handler %s %s" % (policy_name, policy_handler))
        if policy_handler is not None:
            if (deleted):
                try:
                    policy_handler.handle_delete(instance)
                except AttributeError:
                    pass
            else:
                policy_handler.handle(instance)
        logger.debug("MODEL POLICY: completed handler %s %s" % (policy_name, policy_handler))
    except:
        logger.log_exc("MODEL POLICY: Exception when running handler")

    try:
        instance.policed=timezone.now()
        instance.save(update_fields=['policed'])
    except:
        logger.log_exc('MODEL POLICY: Object %r is defective'%instance)
        bad_instances.append(instance)

def noop(o,p):
        pass

def check_db_connection_okay():
    # django implodes if the database connection is closed by docker-compose
    from django import db
    try:
        db.connection.cursor()
        #diag = Diag.objects.filter(name="foo").first()
    except Exception, e:
        if "connection already closed" in traceback.format_exc():
           logger.error("XXX connection already closed")
           try:
#               if db.connection:
#                   db.connection.close()
               db.close_old_connections()
           except:
                logger.log_exc("XXX we failed to fix the failure")
        else:
           logger.log_exc("XXX some other error")

def run_policy():
    load_model_policies()

    while (True):
        start = time.time()
        try:
            run_policy_once()
        except:
            logger.log_exc("MODEL_POLICY: Exception in run_policy()")
        if (time.time()-start<1):
            time.sleep(1)

from core.models.plcorebase import XOSCollector
from django.db import router
def has_deleted_dependencies(m):
    # Check to see if 'm' would cascade to any objects that have the 'deleted'
    # field set in them.
    collector = XOSCollector(using=router.db_for_write(m.__class__, instance=m))
    collector.collect([m])
    deps=[]
    for (k, models) in collector.data.items():
        for model in models:
            if model==m:
                # collector will return ourself; ignore it.
                continue
            if issubclass(m.__class__, model.__class__):
                # collector will return our parent classes; ignore them.
                continue
# We don't actually need this check, as with multiple passes the reaper can
# clean up a hierarchy of objects.
#            if getattr(model, "backend_need_reap", False):
#                # model is already marked for reaping; ignore it.
#                continue
            deps.append(model)
    return deps

def run_policy_once():
        from core.models import Instance,Slice,Controller,Network,User,SlicePrivilege,Site,SitePrivilege,Image,ControllerSlice,ControllerUser,ControllerSite
        models = [Controller, Site, SitePrivilege, Image, ControllerSlice, ControllerSite, ControllerUser, User, Slice, Network, Instance, SlicePrivilege]
        objects = []
        deleted_objects = []

        logger.debug("MODEL POLICY: run_policy_once()")

        check_db_connection_okay()

        for m in models:
            res = m.objects.filter((Q(policed__lt=F('updated')) | Q(policed=None)) & Q(no_policy=False))
            objects.extend(res)
            res = m.deleted_objects.filter(Q(policed__lt=F('updated')) | Q(policed=None))
            deleted_objects.extend(res)

        for o in objects:
            execute_model_policy(o, o.deleted)

        for o in deleted_objects:
            execute_model_policy(o, True)

        # Reap non-sync'd models here
        # models_to_reap = [Slice,Network,NetworkSlice]

        models_to_reap = django_models.get_models(include_auto_created=False)
        for m in models_to_reap:
            if not hasattr(m, "deleted_objects"):
                continue

            dobjs = m.deleted_objects.all()
            for d in dobjs:
                if hasattr(d,"_meta") and hasattr(d._meta,"proxy") and d._meta.proxy:
                    # skip proxy objects; we'll get the base instead
                    continue
                if (not getattr(d, "backend_need_reap", False)) and getattr(d, "backend_need_delete", False):
                    journal_object(d, "reaper.need_delete")
                    print "Reaper: skipping %r because it has need_delete set" % d
                    continue
                deleted_deps = has_deleted_dependencies(d)
                if deleted_deps:
                    journal_object(d, "reaper.has_deleted_dependencies", msg=",".join([str(m) for m in deleted_deps]))
                    print 'Reaper: cannot purge object %r because it has deleted dependencies: %s' % (d, ",".join([str(m) for m in deleted_deps]))
                    continue
                deps = walk_inv_deps(noop, d)
                if (not deps):
                    journal_object(d, "reaper.purge")
                    print 'Reaper: purging object %r'%d
                    d.delete(purge=True)

        try:
            reset_queries()
        except:
            # this shouldn't happen, but in case it does, catch it...
            logger.log_exc("MODEL POLICY: exception in reset_queries")

        logger.debug("MODEL POLICY: finished run_policy_once()")
