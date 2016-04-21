#!/bin/bash

source ./config.sh

TARGET_ID=1
TEST=ping
ARGUMENT=128.112.139.30

echo curl "-H \"Accept: application/json; indent=4\" -H \"Content-Type: application/json\" -u $AUTH -X POST -d \"{\\\"target_id\\\": \\\"$TARGET_ID\\\", \\\"test\\\": \\\"$TEST\\\", \\\"argument\\\": \\\"$ARGUMENT\\\"}\" $HOST/xoslib/truckroll/"

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X POST -d "{\"target_id\": \"$TARGET_ID\", \"test\": \"$TEST\", \"argument\": \"$ARGUMENT\"}" $HOST/xoslib/truckroll/
