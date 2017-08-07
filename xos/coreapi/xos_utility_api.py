
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


import base64
import fnmatch
import os
import sys
import time
import traceback
from protos import utility_pb2
from google.protobuf.empty_pb2 import Empty

from importlib import import_module
from django.conf import settings
SessionStore = import_module(settings.SESSION_ENGINE).SessionStore

from django.contrib.auth import authenticate as django_authenticate
import django.apps
from django.db.models import F,Q
from core.models import *
from xos.exceptions import *
from apihelper import XOSAPIHelperMixin, translate_exceptions

# The Tosca engine expects to be run from /opt/xos/tosca/ or equivalent. It
# needs some sys.path fixing up.
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
toscadir = os.path.join(currentdir, "../tosca")

def is_internal_model(model):
    """ things to be excluded from the dirty_models endpoints """
    if 'django' in model.__module__:
        return True
    if 'cors' in model.__module__:
        return True
    if 'contenttypes' in model.__module__:
        return True
    if 'core.models.journal' in model.__module__:  # why?
        return True
    if 'core.models.project' in model.__module__:  # why?
        return True
    return False

def get_xproto(folder):
    matches = []
    for root, dirnames, filenames in os.walk(folder):
        for filename in fnmatch.filter(filenames, '*.xproto'):
            matches.append(os.path.join(root, filename))
    return matches

class UtilityService(utility_pb2.utilityServicer, XOSAPIHelperMixin):
    def __init__(self, thread_pool):
        self.thread_pool = thread_pool
        XOSAPIHelperMixin.__init__(self)

    def stop(self):
        pass

    @translate_exceptions
    def Login(self, request, context):
        if not request.username:
            raise XOSNotAuthenticated("No username")

        u=django_authenticate(username=request.username, password=request.password)
        if not u:
            raise XOSNotAuthenticated("Failed to authenticate user %s" % request.username)

        session = SessionStore()
        auth = {"username": request.username, "password": request.password}
        session["auth"] = auth
        session['_auth_user_id'] = u.pk
        session['_auth_user_backend'] = u.backend
        session.save()

        response = utility_pb2.LoginResponse()
        response.sessionid = session.session_key

        return response

    @translate_exceptions
    def Logout(self, request, context):
        for (k, v) in context.invocation_metadata():
            if (k.lower()=="x-xossession"):
                s = SessionStore(session_key=v)
                if "_auth_user_id" in s:
                    del s["_auth_user_id"]
                    s.save()
        return Empty()

    @translate_exceptions
    def RunTosca(self, request, context):
        user=self.authenticate(context, required=True)

        sys_path_save = sys.path
        try:
            sys.path.append(toscadir)
            from tosca.engine import XOSTosca
            xt = XOSTosca(request.recipe, parent_dir=toscadir, log_to_console=False)
            xt.execute(user)
        except:
            response = utility_pb2.ToscaResponse()
            response.status = response.ERROR
            response.messages = traceback.format_exc()
            return response
        finally:
            sys.path = sys_path_save

        response = utility_pb2.ToscaResponse()
        response.status = response.SUCCESS
        response.messages = "\n".join(xt.log_msgs)

        return response

    @translate_exceptions
    def DestroyTosca(self, request, context):
        user=self.authenticate(context, required=True)

        sys_path_save = sys.path
        try:
            sys.path.append(toscadir)
            from tosca.engine import XOSTosca
            xt = XOSTosca(request.recipe, parent_dir=toscadir, log_to_console=False)
            xt.destroy(user)
        except:
            response = utility_pb2.ToscaResponse()
            response.status = response.ERROR
            response.messages = traceback.format_exc()
            return response
        finally:
            sys.path = sys_path_save

        response = utility_pb2.ToscaResponse()
        response.status = response.SUCCESS
        response.messages = "\n".join(xt.log_msgs)

        return response

    @translate_exceptions
    def NoOp(self, request, context):
        return Empty()

    @translate_exceptions
    def AuthenticatedNoOp(self, request, context):
        self.authenticate(context, required=True)
        return Empty()

    @translate_exceptions
    def ListDirtyModels(self, request, context):
        dirty_models = utility_pb2.ModelList()

        models = django.apps.apps.get_models()
        for model in models:
            if is_internal_model(model):
                continue
            fieldNames = [x.name for x in model._meta.fields]
            if (not "enacted" in fieldNames) or (not "updated" in fieldNames):
                continue
            if (request.class_name) and (not fnmatch.fnmatch(model.__name__, request.class_name)):
                continue
            objs = model.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))
            for obj in objs:
                item = dirty_models.items.add()
                item.class_name = model.__name__
                item.id = obj.id

        return dirty_models

    @translate_exceptions
    def SetDirtyModels(self, request, context):
        user=self.authenticate(context, required=True)

        dirty_models = utility_pb2.ModelList()

        models = django.apps.apps.get_models()
        for model in models:
            if is_internal_model(model):
                continue
            fieldNames = [x.name for x in model._meta.fields]
            if (not "enacted" in fieldNames) or (not "updated" in fieldNames):
                continue
            if (request.class_name) and (not fnmatch.fnmatch(model.__name__, request.class_name)):
                continue
            objs = model.objects.all()
            for obj in objs:
                try:
                     obj.caller = user
                     obj.save()
                except Exception, e:
                    item = dirty_models.items.add()
                    item.class_name = model.__name__
                    item.id = obj.id
                    item.info = str(e)

        return dirty_models

    @translate_exceptions
    def GetXproto(self, request, context):
        res = utility_pb2.XProtos()

        core_dir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + '/../core/models/')
        core_xprotos = get_xproto(core_dir)

        service_dir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + '/../services')
        services_xprotos = get_xproto(service_dir)

        xprotos = core_xprotos + services_xprotos

        xproto = ""

        for f in xprotos:
            content = open(f).read()
            xproto += "\n"
            xproto += content

        res.xproto = xproto
        return res

