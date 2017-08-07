
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


import sys
sys.path.append("..")

from xosapi import xos_grpc_client

def test_callback():
    print "TEST: csr_introspect"

    c = xos_grpc_client.coreclient

    for csr in c.xos_orm.CordSubscriberRoot.objects.all():
        print "  csr", csr.id
        for field_name in ["firewall_enable", "firewall_rules", "url_filter_enable", "url_filter_rules", "cdn_enable", "uplink_speed", "downlink_speed", "enable_uverse", "status"]:
            print "    %s: %s" % (field_name, getattr(csr, field_name))

    print "    okay"

xos_grpc_client.start_api_parseargs(test_callback)

