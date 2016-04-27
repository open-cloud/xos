from django.db.models.signals import post_save
from django.dispatch import receiver
import pdb
from generate.dependency_walker import *
from synchronizers.openstack import model_policies
from xos.logger import logger
from datetime import datetime
import time
from core.models import *
from django.db import reset_queries
from django.db.transaction import atomic
from django.db.models import F, Q

modelPolicyEnabled = True
bad_instances=[]

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
        raise e
    except Exception,e:
            logger.info('Could not save %r. Exception: %r'%(d,e), extra=d.tologdict())

def delete_if_inactive(d, o):
    try:
        d.delete()
        print "Deleted %s (%s)"%(d,d.__class__.__name__)
    except:
        pass
    return


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
        policy_handler = getattr(model_policies, policy_name, None)
        logger.error("POLICY HANDLER: %s %s" % (policy_name, policy_handler))
        if policy_handler is not None:
            if (deleted):
                try:
                    policy_handler.handle_delete(instance)
                except AttributeError:
                    pass
            else:
                policy_handler.handle(instance)
    except:
        logger.log_exc("Model Policy Error:")

    try:
        instance.policed=datetime.now()
        instance.save(update_fields=['policed'])
    except:
        logging.error('Object %r is defective'%instance)
        bad_instances.append(instance)

def noop(o,p):
        pass

def run_policy():
    while (True):
        start = time.time()
        run_policy_once()
        if (time.time()-start<1):
            time.sleep(1)

def run_policy_once():
        from core.models import Instance,Slice,Controller,Network,User,SlicePrivilege,Site,SitePrivilege,Image,ControllerSlice,ControllerUser,ControllerSite
        models = [Controller, Site, SitePrivilege, Image, ControllerSlice, ControllerSite, ControllerUser, User, Slice, Network, Instance, SlicePrivilege]
        objects = []
        deleted_objects = []

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
        reaped = [Slice]

        for m in reaped:
            dobjs = m.deleted_objects.all()
            for d in dobjs:
                deps = walk_inv_deps(noop, d)
                if (not deps):
                    print 'Purging object %r'%d
                    d.delete(purge=True)

        try:
            reset_queries()
        except:
            # this shouldn't happen, but in case it does, catch it...
            logger.log_exc("exception in reset_queries")
