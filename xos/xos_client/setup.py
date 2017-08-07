
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


#! /usr/bin/env python

import os
import sys
import site
from distutils.core import setup

CHAMELEON_DIR='xosapi/chameleon'

if not os.path.exists(CHAMELEON_DIR):
    raise Exception("%s does not exist!" % CHAMELEON_DIR)

if not os.path.exists(os.path.join(CHAMELEON_DIR, "protos/schema_pb2.py")):
    raise Exception("Please make the chameleon protos")

setup(name='xosapi',
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

# If we're not running a Virtual Env
if not hasattr(sys, 'real_prefix'):
    # Chameleon needs the following files set as executable
    for dir in site.getsitepackages():
       fn = os.path.join(dir, "xosapi/chameleon/protoc_plugins/gw_gen.py")
       if os.path.exists(fn):
           os.chmod(fn, 0777)
       fn = os.path.join(dir, "xosapi/chameleon/protoc_plugins/swagger_gen.py")
       if os.path.exists(fn):
           os.chmod(fn, 0777)


"""
from twisted.internet import reactor
from xosapi.xos_grpc_client import InsecureClient
client = InsecureClient(endpoint="xos-core.cord.lab:50055")
client.start()
reactor.run()
"""


