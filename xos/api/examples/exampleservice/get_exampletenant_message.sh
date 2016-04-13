#!/bin/bash

# this example illustrates using a custom REST API endpoint

source ./config.sh

if [[ "$#" -ne 1 ]]; then
    echo "Syntax: get_exampletenant_message.sh <id>"
    exit -1
fi

ID=$1

curl -H "Accept: application/json; indent=4" -u $AUTH -X GET $HOST/api/tenant/exampletenant/$ID/message/
