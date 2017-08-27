
# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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

import pdb
import time
import traceback

modelPolicyEnabled = True
bad_instances=[]

model_policies = {}

from xosconfig import Config
from multistructlog import create_logger

Config.init()
log = create_logger(Config().get('logging'))

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
        log.exception("AttributeError in update_dep", e = e)
        raise e
    except Exception,e:
        log.exception("Exception in update_dep", e = e)

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
        log.debug("MODEL POLICY: handler %s %s",policy_name = policy_name, policy_handler = policy_handler)
        if policy_handler is not None:
            if (deleted):
                try:
                    policy_handler.handle_delete(instance)
                except AttributeError:
                    pass
            else:
                policy_handler.handle(instance)
        log.debug("MODEL POLICY: completed handler", policy_name = policy_name, policy_handler = policy_handler)
    except Exception, e:
        log.exception("MODEL POLICY: Exception when running handler", e = e)

    try:
        instance.policed=timezone.now()
        instance.save(update_fields=['policed'])
    except:
        log.exception('MODEL POLICY: Object is defective', object = instance)
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
           log.error("XXX connection already closed")
           try:
#               if db.connection:
#                   db.connection.close()
               db.close_old_connections()
           except Exception,f:
               log.exception("XXX we failed to fix the failure", e = f)
        else:
           log.exception("XXX some other error", e = e)

def run_policy():
    load_model_policies()

    while (True):
        start = time.time()
        try:
            run_policy_once()
        except Exception,e:
            log.exception("MODEL_POLICY: Exception in run_policy()", e)

        if (time.time()-start<1):
            time.sleep(1)

def run_policy_once():
        from core.models import Instance,Slice,Controller,Network,User,SlicePrivilege,Site,SitePrivilege,Image,ControllerSlice,ControllerUser,ControllerSite
        models = [Controller, Site, SitePrivilege, Image, ControllerSlice, ControllerSite, ControllerUser, User, Slice, Network, Instance, SlicePrivilege, Privilege]
        objects = []
        deleted_objects = []

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

        try:
            reset_queries()
        except Exception,e:
            # this shouldn't happen, but in case it does, catch it...
            log.exception("MODEL POLICY: exception in reset_queries", e = e)
