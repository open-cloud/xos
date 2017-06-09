from synchronizers.new_base.modelaccessor import *
from synchronizers.new_base.dependency_walker_new import *
from synchronizers.new_base.policy import Policy
from xos.logger import Logger, logging

import imp
import pdb
import time
import traceback

logger = Logger(level=logging.DEBUG)

class XOSPolicyEngine(object):
    def __init__(self, policies_dir):
        self.model_policies = self.load_model_policies(policies_dir)
        self.policies_by_name = {}
        self.policies_by_class = {}

        for policy in self.model_policies:
            if not policy.model_name in self.policies_by_name:
                self.policies_by_name[policy.model_name] = []
            self.policies_by_name[policy.model_name].append(policy)

            if not policy.model in self.policies_by_class:
                self.policies_by_class[policy.model] = []
            self.policies_by_class[policy.model].append(policy)

    def update_wp(self, d, o):
        try:
            save_fields = []
            if (d.write_protect != o.write_protect):
                d.write_protect = o.write_protect
                save_fields.append('write_protect')
            if (save_fields):
                d.save(update_fields=save_fields)
        except AttributeError,e:
            raise e

    def update_dep(self, d, o):
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

    def delete_if_inactive(self, d, o):
        try:
            d.delete()
            print "Deleted %s (%s)"%(d,d.__class__.__name__)
        except:
            pass
        return

    def load_model_policies(self, policies_dir):
        policies=[]
        for fn in os.listdir(policies_dir):
                if fn.startswith("test"):
                    # don't try to import unit tests!
                    continue
                pathname = os.path.join(policies_dir,fn)
                if os.path.isfile(pathname) and fn.endswith(".py") and (fn!="__init__.py"):
                    module = imp.load_source(fn[:-3], pathname)
                    for classname in dir(module):
                        c = getattr(module, classname, None)

                        # make sure 'c' is a descendent of Policy and has a
                        # provides field (this eliminates the abstract base classes
                        # since they don't have a provides)

                        if inspect.isclass(c) and issubclass(c, Policy) and hasattr(c, "model_name") and (
                            c not in policies):
                            if not c.model_name:
                                logger.info("load_model_policies: skipping model policy %s" % classname)
                                continue
                            if not model_accessor.has_model_class(c.model_name):
                                logger.error("load_model_policies: unable to find policy %s model %s" % (classname, c.model_name))
                            c.model = model_accessor.get_model_class(c.model_name)
                            policies.append(c)

        logger.info("Loaded %s model policies" % len(policies))
        return policies

    def execute_model_policy(self, instance, action):
        # These are the models whose children get deleted when they are
        delete_policy_models = ['Slice','Instance','Network']
        sender_name = getattr(instance, "model_name", instance.__class__.__name__)
        new_policed = model_accessor.now()

        #if (action != "deleted"):
        #    walk_inv_deps(self.update_dep, instance)
        #    walk_deps(self.update_wp, instance)
        #elif (sender_name in delete_policy_models):
        #    walk_inv_deps(self.delete_if_inactive, instance)

        policies_failed = False
        for policy in self.policies_by_name.get(sender_name, None):
            method_name= "handle_%s" % action
            if hasattr(policy, method_name):
                try:
                    logger.debug("MODEL POLICY: calling handler %s %s %s %s" % (sender_name, instance, policy.__name__, method_name))
                    getattr(policy(), method_name)(instance)
                    logger.debug("MODEL POLICY: completed handler %s %s %s %s" % (sender_name, instance, policy.__name__, method_name))
                except:
                    logger.log_exc("MODEL POLICY: Exception when running handler")
                    policies_failed = True

                    try:
                        instance.policy_status = "2 - %s" % traceback.format_exc(limit=1)
                        instance.save(update_fields=["policy_status"])
                    except:
                        logger.log_exc("MODEL_POLICY: Exception when storing policy_status")

        if not policies_failed:
            try:
                instance.policed=new_policed
                instance.policy_status = "1 - done"
                instance.save(update_fields=['policed', 'policy_status'])
            except:
                logger.log_exc('MODEL POLICY: Object %r failed to update policed timestamp' % instance)

    def noop(self, o,p):
            pass

    def run(self):
        while (True):
            start = time.time()
            try:
                self.run_policy_once()
            except:
                logger.log_exc("MODEL_POLICY: Exception in run()")
            if (time.time() - start < 5):
                time.sleep(5)

    # TODO: This loop is different from the synchronizer event_loop, but they both do mostly the same thing. Look for
    # ways to combine them.

    def run_policy_once(self):
            models = self.policies_by_class.keys()

            logger.debug("MODEL POLICY: run_policy_once()")

            model_accessor.check_db_connection_okay()

            objects = model_accessor.fetch_policies(models, False)
            deleted_objects = model_accessor.fetch_policies(models, True)

            for o in objects:
                if o.deleted:
                    # This shouldn't happen, but previous code was examining o.deleted. Verify.
                    continue
                if not o.policed:
                    self.execute_model_policy(o, "create")
                else:
                    self.execute_model_policy(o, "update")

            for o in deleted_objects:
                self.execute_model_policy(o, "delete")

            try:
                model_accessor.reset_queries()
            except:
                # this shouldn't happen, but in case it does, catch it...
                logger.log_exc("MODEL POLICY: exception in reset_queries")

            logger.debug("MODEL POLICY: finished run_policy_once()")
