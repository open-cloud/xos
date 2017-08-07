
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


#!/bin/bash

# this example illustrates using a custom REST API endpoint  

source ./config.sh

if [[ "$#" -ne 2 ]]; then
    echo "Syntax: put_exampletenant_message.sh <id> <message>"
    exit -1
fi

ID=$1
NEW_MESSAGE=$2

DATA=$(cat <<EOF
{"tenant_message": "$NEW_MESSAGE"}
EOF
)

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X PUT -d "$DATA" $HOST/api/tenant/exampletenant/$ID/message/
