#!/bin/bash

source ./config.sh

if [[ "$#" -ne 1 ]]; then
    echo "Syntax: delete_truckroll.sh <id>"
    exit -1
fi

ID=$1

curl -H "Accept: application/json; indent=4" -u $AUTH -X DELETE $HOST/api/tenant/truckroll/$ID/
