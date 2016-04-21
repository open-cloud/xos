#!/bin/bash

source ./config.sh

DATA=$(cat <<EOF
{"tenant_message": "This is a test"}
EOF
)

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X POST -d "$DATA" $HOST/api/tenant/exampletenant/   
