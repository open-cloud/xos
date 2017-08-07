
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


source /opt/xos/coreapi/tests/testconfig-chameleon.sh

RESPONSE=`curl -X POST -H "Content-Type: application/json" -d "{\"username\": \"$USERNAME\", \"password\": \"$PASSWORD\"}" http://$HOSTNAME:8080/xosapi/v1/utility/login`
SESSIONID=`echo $RESPONSE | python -c "import json,sys; print json.load(sys.stdin)['sessionid']"`
echo "sessionid=$SESSIONID"

RS=`cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1`
SLICENAME="mysite_$RS"

echo "slicename=$SLICENAME"

RESPONSE=`curl -X POST -H "x-xossession: $SESSIONID" -H "Content-Type: application/json" -d "{\"name\": \"$SLICENAME\", \"site_id\": 1}" http://$HOSTNAME:8080/xosapi/v1/core/slices`

echo "create response: $RESPONSE"
SLICEID=`echo $RESPONSE | python -c "import json,sys; print json.load(sys.stdin)['id']"`

RESPONSE=`curl -X GET -H "x-xossession: $SESSIONID" http://$HOSTNAME:8080/xosapi/v1/core/slices/$SLICEID`
echo "get response: $RESPONSE"

RESPONSE=`curl -X DELETE -H "x-xossession: $SESSIONID" http://$HOSTNAME:8080/xosapi/v1/core/slices/$SLICEID`

echo "delete response: $RESPONSE"
