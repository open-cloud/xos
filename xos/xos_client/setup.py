#!/usr/bin/env python

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
import sys
import site
from setuptools.command.install import install


try:
    from xosutil.autoversion_setup import setup_with_auto_version as setup
except ImportError:
    # xosutil is not installed. Expect this to happen when we build an egg, in which case xosgenx.version will
    # automatically have the right version.
    from setuptools import setup

from xosapi.version import __version__

CHAMELEON_DIR='xosapi/chameleon'

if not os.path.exists(CHAMELEON_DIR):
    raise Exception("%s does not exist!" % CHAMELEON_DIR)

if not os.path.exists(os.path.join(CHAMELEON_DIR, "protos/schema_pb2.py")):
    raise Exception("Please make the chameleon protos")

# Chameleon requires these files have executable permission set.
class InstallFixChameleonPermissions(install):
    def run(self):
        install.run(self)
        for filepath in self.get_outputs():
            if filepath.endswith("chameleon/protoc_plugins/gw_gen.py") or \
               filepath.endswith("chameleon/protoc_plugins/swagger_gen.py"):
               os.chmod(filepath, 0777)

setup_result = setup(name='xosapi',
      version=__version__,
      cmdclass={"install": InstallFixChameleonPermissions},
      description='XOS api client',
      package_dir= {'xosapi.chameleon': CHAMELEON_DIR},
      packages=['xosapi.chameleon.grpc_client',
                'xosapi.chameleon.protos',
                'xosapi.chameleon.protos.third_party',
                'xosapi.chameleon.protos.third_party.google',
                'xosapi.chameleon.protos.third_party.google.api',
                'xosapi.chameleon.utils',
                'xosapi.chameleon.protoc_plugins',
                'xosapi',
                'xosapi.convenience'],
      py_modules= ['xosapi.chameleon.__init__'],
      include_package_data=True,
      package_data = {'xosapi.chameleon.protos.third_party.google.api': ['*.proto'],
                      'xosapi.chameleon.protos': ['*.proto'],
                      'xosapi.chameleon.protoc_plugins': ['*.desc']},
      scripts = ['xossh'],
     )



