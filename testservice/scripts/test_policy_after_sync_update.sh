#!/bin/bash

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

set -e

CHAMELEON_URL=http://`hostname`:30006/xosapi/v1/testservice/testserviceserviceinstances
TOSCA_URL=http://`hostname`:30007
TEST_POD=`kubectl get pods | grep -i testservice | cut -f 1 -d " "`
RECIPE=../tosca/test_policy_after_sync_update.yaml

curl -H "xos-username: admin@opencord.org" -H "xos-password: letmein" -X post --data-binary @$RECIPE $TOSCA_URL/run

echo "done tosca"

cat <<EOF > wait_for.txt
TEST:SYNC_DONE                 id=[0-9]+ model_class=TestserviceServiceInstance model_name=u'test-policy-after-sync-update' some_integer=0 some_other_integer=0
TEST:SYNC_DONE                 id=[0-9]+ model_class=TestserviceServiceInstance model_name=u'test-policy-after-sync-update' some_integer=0 some_other_integer=1
TEST:POLICY_DONE               id=[0-9]+ model_class=TestserviceServiceInstance model_name=u'test-policy-after-sync-update' some_integer=0 some_other_integer=1
EOF
kubectl logs -f --since=30s $TEST_POD | ansi2txt | python wait_for_lines.py wait_for.txt

python ./verify_model.py $CHAMELEON_URL name=test-policy-after-sync-update "updated>=0" "policed>=@updated" "enacted>=@policed" "some_other_integer=1"
