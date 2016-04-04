#!/bin/bash

source ./config.sh
source ./util.sh

ACCOUNT_NUM=1238

SUBSCRIBER_ID=$(lookup_account_num $ACCOUNT_NUM)
if [[ $? != 0 ]]; then
    exit -1
fi

VOLT_ID=$(lookup_subscriber_volt $SUBSCRIBER_ID)
if [[ $? != 0 ]]; then
    exit -1
fi

curl -u $AUTH -X DELETE $HOST/api/tenant/cord/volt/$VOLT_ID/
