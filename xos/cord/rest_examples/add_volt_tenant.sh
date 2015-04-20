#!/bin/bash

HOST=198.0.0.44:8000
AUTH=scott@onlab.us:letmein
SERVICE_SPECIFIC_ID=5678
VLAN_ID=1234

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X POST -d "{\"service_specific_id\": \"$SERVICE_SPECIFIC_ID\", \"vlan_id\": \"$VLAN_ID\"}" $HOST/xoslib/volttenant/  
