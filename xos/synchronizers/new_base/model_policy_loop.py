from synchronizers.new_base.modelaccessor import *
from synchronizers.new_base.dependency_walker_new import *
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

def execute_model_policy(instance, deleted):
    # Automatic dirtying
    if (instance in bad_instances):
        return

    # These are the models whose children get deleted when they are
    delete_policy_models = ['Slice','Instance','Network']
    sender_name = getattr(instance, "model_name", instance.__class__.__name__)
    policy_name = 'model_policy_%s'%sender_name
    noargs = False

    if (not deleted):
        walk_inv_deps(update_dep, instance)
        walk_deps(update_wp, instance)
    elif (sender_name in delete_policy_models):
        walk_inv_deps(delete_if_inactive, instance)

    try:
        policy_handler = model_policies.get(policy_name, None)
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
        instance.policed=model_accessor.now()
        instance.save(update_fields=['policed'])
    except:
        logger.log_exc('MODEL POLICY: Object %r is defective'%instance)
        bad_instances.append(instance)

def noop(o,p):
        pass

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

def run_policy_once():
        # TODO: Core-specific model list is hardcoded here. These models should
        # be learned from the model_policy files, not hardcoded.

        models = [Controller, Site, SitePrivilege, Image, ControllerSlice, ControllerSite, ControllerUser, User, Slice, Network, Instance, SlicePrivilege]

        logger.debug("MODEL POLICY: run_policy_once()")

        model_accessor.check_db_connection_okay()

        objects = model_accessor.fetch_policies(models, False)
        deleted_objects = model_accessor.fetch_policies(models, True)

        for o in objects:
            execute_model_policy(o, o.deleted)

        for o in deleted_objects:
            execute_model_policy(o, True)

        try:
            model_accessor.reset_queries()
        except:
            # this shouldn't happen, but in case it does, catch it...
            logger.log_exc("MODEL POLICY: exception in reset_queries")

        logger.debug("MODEL POLICY: finished run_policy_once()")
