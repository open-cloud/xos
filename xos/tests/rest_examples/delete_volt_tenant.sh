#!/bin/bash

source ./config.sh

ID=89

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X DELETE $HOST/xoslib/volttenant/$ID/  
