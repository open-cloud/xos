#!/bin/bash

source ./config.sh
source ./util.sh

ACCOUNT_NUM=1238

SUBSCRIBER_ID=$(lookup_account_num $ACCOUNT_NUM)
if [[ $? != 0 ]]; then
    exit -1
fi

VSG_ID=$(lookup_subscriber_vsg $SUBSCRIBER_ID)
if [[ $? != 0 ]]; then
    exit -1
fi

DATA=$(cat <<EOF
{"target_id": $SUBSCRIBER_ID,
 "scope": "container",
 "test": "ping",
 "argument": "8.8.8.8"}
EOF
)

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X POST -d "$DATA" $HOST/api/tenant/truckroll/
