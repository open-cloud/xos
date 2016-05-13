#!/bin/bash

source ./config.sh
source ./util.sh

ACCOUNT_NUM=1238
MAC="19:28:37:46:55"

SUBSCRIBER_ID=$(lookup_account_num $ACCOUNT_NUM)
if [[ $? != 0 ]]; then
    exit -1
fi

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X GET $HOST/api/tenant/cord/subscriber/$SUBSCRIBER_ID/devices/$MAC/features/uplink_speed/
