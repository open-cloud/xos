#!/bin/bash

source ./config.sh

if [[ "$#" -ne 1 ]]; then
    echo "Syntax: delete_exampletenant.sh <id>"
    exit -1
fi

ID=$1

curl -H "Accept: application/json; indent=4" -u $AUTH -X DELETE $HOST/api/tenant/exampletenant/$ID/
