
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


""" ModelAccessor

    A class for abstracting access to models. Used to get any djangoisms out
    of the synchronizer code base.

    This module will import all models into this module's global scope, so doing
    a "from modelaccessor import *" from a calling module ought to import all
    models into the calling module's scope.
"""

import functools
import os
import signal
from xosconfig import Config
from diag import update_diag

from xosconfig import Config
from multistructlog import create_logger

log = create_logger(Config().get('logging'))

orig_sigint = None
model_accessor = None


class ModelAccessor(object):
    def __init__(self):
        self.all_model_classes = self.get_all_model_classes()

    def get_all_model_classes(self):
        """ Build a dictionary of all model class names """
        raise Exception("Not Implemented")

    def get_model_class(self, name):
        """ Given a class name, return that model class """
        return self.all_model_classes[name]

    def has_model_class(self, name):
        """ Given a class name, return that model class """
        return name in self.all_model_classes

    def fetch_pending(self, main_objs, deletion=False):
        """ Execute the default fetch_pending query """
        raise Exception("Not Implemented")

    def fetch_policies(self, main_objs, deletion=False):
        """ Execute the default fetch_pending query """
        raise Exception("Not Implemented")

    def reset_queries(self):
        """ Reset any state between passes of synchronizer. For django, to
            limit memory consumption of cached queries.
        """
        pass

    def connection_close(self):
        """ Close any active database connection. For django, to limit memory
            consumption.
        """
        pass

    def check_db_connection_okay(self):
        """ Checks to make sure the db connection is okay """
        pass

    def obj_exists(self, o):
        """ Return True if the object exists in the data model """
        raise Exception("Not Implemented")

    def obj_in_list(self, o, olist):
        """ Return True if o is the same as one of the objects in olist """
        raise Exception("Not Implemented")

    def now(self):
        """ Return the current time for timestamping purposes """
        raise Exception("Not Implemented")

    def update_diag(self, loop_end=None, loop_start=None, syncrecord_start=None, sync_start=None, backend_status=None, backend_code=0):
        if self.has_model_class("Diag"):
            return update_diag(self.get_model_class("Diag"), loop_end, loop_start, syncrecord_start, sync_start,
                               backend_status,backend_code=0)

    def is_type(self, obj, name):
        """ returns True is obj is of model type "name" """
        raise Exception("Not Implemented")

    def is_instance(self, obj, name):
        """ returns True if obj is of model type "name" or is a descendant """
        raise Exception("Not Implemented")

    def get_content_type_id(self, obj):
        raise Exception("Not Implemented")

    def journal_object(self, o, operation, msg=None, timestamp=None):
        pass

    def create_obj(self, cls, **kwargs):
        raise Exception("Not Implemented")


def import_models_to_globals():
    # add all models to globals
    for (k, v) in model_accessor.all_model_classes.items():
        globals()[k] = v

    # xosbase doesn't exist from the synchronizer's perspective, so fake out
    # ModelLink.
    if "ModelLink" not in globals():
        class ModelLink:
            def __init__(self, dest, via, into=None):
                self.dest = dest
                self.via = via
                self.into = into

        globals()["ModelLink"] = ModelLink


def keep_trying(client, reactor):
    # Keep checking the connection to wait for it to become unavailable.
    # Then reconnect.

    # logger.info("keep_trying")   # message is unneccesarily verbose

    from xosapi.xos_grpc_client import Empty

    try:
        client.utility.NoOp(Empty())
    except Exception,e:
        # If we caught an exception, then the API has become unavailable.
        # So reconnect.

        log.exception("exception in NoOp", e)
        client.connected = False
        client.connect()
        return

    reactor.callLater(1, functools.partial(keep_trying, client, reactor))


def grpcapi_reconnect(client, reactor):
    global model_accessor

    # this will prevent updated timestamps from being automatically updated
    client.xos_orm.caller_kind = "synchronizer"

    from apiaccessor import CoreApiModelAccessor
    model_accessor = CoreApiModelAccessor(orm=client.xos_orm)

    # If required_models is set, then check to make sure the required_models
    # are present. If not, then the synchronizer needs to go to sleep until
    # the models show up.

    required_models = Config.get("required_models")
    if required_models:
        required_models = [x.strip() for x in required_models]

        missing = []
        found = []
        for model in required_models:
            if model_accessor.has_model_class(model):
                found.append(model)
            else:
                missing.append(model)

        log.info("required_models, found:", models =  ", ".join(found))
        if missing:
            log.warning("required_models: missing",models = ", ".join(missing))
            # We're missing a required model. Give up and wait for the connection
            # to reconnect, and hope our missing model has shown up.
            reactor.callLater(1, functools.partial(keep_trying, client, reactor))
            return

    # import all models to global space
    import_models_to_globals()

    # Synchronizer framework isn't ready to embrace reactor yet...
    reactor.stop()

    # Restore the sigint handler
    signal.signal(signal.SIGINT, orig_sigint)


def config_accessor_grpcapi():
    global orig_sigint

    grpcapi_endpoint = Config.get("accessor.endpoint")
    grpcapi_username = Config.get("accessor.username")
    grpcapi_password = Config.get("accessor.password")

    # if password starts with "@", then retreive the password from a file
    if grpcapi_password.startswith("@"):
        fn = grpcapi_password[1:]
        if not os.path.exists(fn):
            raise Exception("%s does not exist" % fn)
        grpcapi_password = open(fn).readline().strip()

    from xosapi.xos_grpc_client import SecureClient
    from twisted.internet import reactor

    grpcapi_client = SecureClient(endpoint=grpcapi_endpoint, username=grpcapi_username, password=grpcapi_password)
    grpcapi_client.set_reconnect_callback(functools.partial(grpcapi_reconnect, grpcapi_client, reactor))
    grpcapi_client.start()

    # Start reactor. This will cause the client to connect and then execute
    # grpcapi_callback().

    # Reactor will take over SIGINT during reactor.run(), but does not return it when reactor.stop() is called.

    orig_sigint = signal.getsignal(signal.SIGINT)

    # Start reactor. This will cause the client to connect and then execute
    # grpcapi_callback().

    reactor.run()

def config_accessor():
    accessor_kind = Config.get("accessor.kind")

    if accessor_kind == "testframework":
        pass
    elif accessor_kind == "grpcapi":
        config_accessor_grpcapi()
    else:
        raise Exception("Unknown accessor kind %s" % accessor_kind)

config_accessor()
