#!/bin/bash

source ./config.sh
source ./util.sh

ACCOUNT_NUM=1238

SUBSCRIBER_ID=$(lookup_account_num $ACCOUNT_NUM)
if [[ $? != 0 ]]; then
    exit -1
fi

DATA=$(cat <<EOF
{"features": {"uplink_speed": 4000000000}}
EOF
)

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X PUT -d "$DATA" $HOST/api/tenant/cord/subscriber/$SUBSCRIBER_ID/
