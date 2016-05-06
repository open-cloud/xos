#!/bin/bash

source ./config.sh
source ./util.sh

ACCOUNT_NUM=1238
MAC="19:28:37:46:55"

SUBSCRIBER_ID=$(lookup_account_num $ACCOUNT_NUM)
if [[ $? != 0 ]]; then
    exit -1
fi

DATA=$(cat <<EOF
{"name": "foo"}
EOF
)

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X PUT -d "$DATA" $HOST/api/tenant/cord/subscriber/$SUBSCRIBER_ID/devices/$MAC/identity/name/
