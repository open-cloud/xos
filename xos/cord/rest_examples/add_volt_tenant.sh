#!/bin/bash

source ./config.sh

SERVICE_SPECIFIC_ID=1238
VLAN_ID=1238

echo curl "-H \"Accept: application/json; indent=4\" -H \"Content-Type: application/json\" -u $AUTH -X POST -d \"{\\\"service_specific_id\\\": \\\"$SERVICE_SPECIFIC_ID\\\", \\\"vlan_id\\\": \\\"$VLAN_ID\\\"}\" $HOST/xoslib/volttenant/"

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X POST -d "{\"service_specific_id\": \"$SERVICE_SPECIFIC_ID\", \"vlan_id\": \"$VLAN_ID\"}" $HOST/xoslib/volttenant/  
