
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


#! /bin/bash

# Run the tests from the head-node against an xos-client VM

PW=`cat /opt/cord/build/platform-install/credentials/xosadmin@opencord.org`

docker run -it --entrypoint python xosproject/xos-client /tmp/xos_client/tests/orm_user_crud.py -u xosadmin@opencord.org -p $PW -qq
docker run -it --entrypoint python xosproject/xos-client /tmp/xos_client/tests/orm_listall.py -u xosadmin@opencord.org -p $PW -qq
docker run -it --entrypoint python xosproject/xos-client /tmp/xos_client/tests/vtr_crud.py -u xosadmin@opencord.org -p $PW -qq
docker run -it --entrypoint python xosproject/xos-client /tmp/xos_client/tests/vsg_introspect.py -u xosadmin@opencord.org -p $PW -qq
docker run -it --entrypoint python xosproject/xos-client /tmp/xos_client/tests/csr_introspect.py -u xosadmin@opencord.org -p $PW -qq