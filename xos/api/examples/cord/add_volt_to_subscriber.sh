#!/bin/bash

source ./config.sh
source ./util.sh

ACCOUNT_NUM=1238
S_TAG=34
C_TAG=134

SUBSCRIBER_ID=$(lookup_account_num $ACCOUNT_NUM)
if [[ $? != 0 ]]; then
    exit -1
fi

DATA=$(cat <<EOF
{"s_tag": $S_TAG,
 "c_tag": $C_TAG,
 "subscriber": $SUBSCRIBER_ID}
EOF
)

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X POST -d "$DATA" $HOST/api/tenant/cord/volt/
