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

import os
from xosconfig import Config
from multistructlog import create_logger

log = create_logger(Config().get("logging"))


class ModelLoadClient(object):
    def __init__(self, api):
        self.api = api

    def upload_models(self, name, dir, version="unknown"):
        request = self.api.dynamicload_pb2.LoadModelsRequest(name=name, version=version)

        for fn in os.listdir(dir):
            if fn.endswith(".xproto"):
                item = request.xprotos.add()
                item.filename = fn
                item.contents = open(os.path.join(dir, fn)).read()

        models_fn = os.path.join(dir, "models.py")
        if os.path.exists(models_fn):
            item = request.decls.add()
            item.filename = "models.py"
            item.contents = open(models_fn).read()

        attic_dir = os.path.join(dir, "attic")
        if os.path.exists(attic_dir):
            log.warn(
                "Attics are deprecated, please use the legacy=True option in xProto"
            )
            for fn in os.listdir(attic_dir):
                if fn.endswith(".py"):
                    item = request.attics.add()
                    item.filename = fn
                    item.contents = open(os.path.join(attic_dir, fn)).read()

        api_convenience_dir = os.path.join(dir, "convenience")
        if os.path.exists(api_convenience_dir):
            for fn in os.listdir(api_convenience_dir):
                if fn.endswith(".py") and "test" not in fn:
                    item = request.convenience_methods.add()
                    item.filename = fn
                    item.contents = open(os.path.join(api_convenience_dir, fn)).read()

        # migrations directory is a sibling to the models directory
        migrations_dir = os.path.join(dir, "..", "migrations")
        if os.path.exists(migrations_dir):
            for fn in os.listdir(migrations_dir):
                if fn.endswith(".py") and "test" not in fn:
                    item = request.migrations.add()
                    item.filename = fn
                    item.contents = open(os.path.join(migrations_dir, fn)).read()

        result = self.api.dynamicload.LoadModels(request)
