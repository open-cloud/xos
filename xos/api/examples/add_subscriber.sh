#!/bin/bash

source ./config.sh

ACCOUNT_NUM=1238

DATA=$(cat <<EOF
{"identity": {"account_num": "$ACCOUNT_NUM", "name": "test-subscriber"},
 "features": {"uplink_speed": 2000000000}}
EOF
)

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X POST -d "$DATA" $HOST/api/tenant/cord/subscriber/   
