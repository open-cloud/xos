#!/bin/bash

source ./config.sh
source ./util.sh

SLICE_NAME=mysite_test1

SLICE_ID=$(lookup_slice_id $SLICE_NAME)
if [[ $? != 0 ]]; then
    exit -1
fi

curl -u $AUTH -X DELETE $HOST/xos/slices/$SLICE_ID/
