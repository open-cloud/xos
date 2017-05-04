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

