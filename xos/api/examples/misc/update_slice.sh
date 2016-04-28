#!/bin/bash

source ./config.sh
source ./util.sh

SLICE_NAME=mysite_test1

SLICE_ID=$(lookup_slice_id $SLICE_NAME)
if [[ $? != 0 ]]; then
    exit -1
fi

DATA=$(cat <<EOF
{"description": "foo"}
EOF
)

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X PATCH -d "$DATA" $HOST/xos/slices/$SLICE_ID/
