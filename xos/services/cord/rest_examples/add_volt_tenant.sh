#!/bin/bash

source ./config.sh

SERVICE_SPECIFIC_ID=1238
C_TAG=1238
S_TAG=3333

echo curl "-H \"Accept: application/json; indent=4\" -H \"Content-Type: application/json\" -u $AUTH -X POST -d \"{\\\"service_specific_id\\\": \\\"$SERVICE_SPECIFIC_ID\\\", \\\"c_tag\\\": \\\"$C_TAG\\\", \\\"s_tag\\\": \\\"$S_TAG\\\"}\" $HOST/xoslib/volttenant/"

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X POST -d "{\"service_specific_id\": \"$SERVICE_SPECIFIC_ID\", \"c_tag\": \"$C_TAG\", \"s_tag\": \"$S_TAG\"}" $HOST/xoslib/volttenant/  
