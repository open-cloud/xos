#!/bin/bash

source ./config.sh

ACCOUNT_NUM=1238
C_TAG=133
S_TAG=33

DATA=$(cat <<EOF
{"identity": {"account_num": "$ACCOUNT_NUM"},
 "features": {"uplink_speed": 2000000000}}
EOF
)

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X POST -d "$DATA" $HOST/api/tenant/cord/subscriber/   
