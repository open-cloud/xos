#!/bin/bash

source ./config.sh

if [[ "$#" -ne 2 ]]; then
    echo "Syntax: delete_exampletenant.sh <id> <message>"
    exit -1
fi

ID=$1
NEW_MESSAGE=$2

DATA=$(cat <<EOF
{"tenant_message": "$NEW_MESSAGE"}
EOF
)

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X PUT -d "$DATA" $HOST/api/tenant/exampletenant/$ID/
