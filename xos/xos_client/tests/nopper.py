
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


""" nopper

    Sends NoOp operations to Core API Server at maximum rate and reports
    performance.
"""

import sys
import time
sys.path.append("..")

from xosapi import xos_grpc_client

def test_callback():
    print "TEST: nop"

    c = xos_grpc_client.coreclient

    while True:
        tStart = time.time()
        count = 0
        while True:
            if type(xos_grpc_client.coreclient) == xos_grpc_client.SecureClient:
               c.utility.AuthenticatedNoOp(xos_grpc_client.Empty())
            else:
               c.utility.NoOp(xos_grpc_client.Empty())
            count = count + 1
            elap = time.time()-tStart
            if (elap >= 10):
                print "nops/second = %d" % int(count/elap)
                tStart = time.time()
                count = 0

xos_grpc_client.start_api_parseargs(test_callback)

