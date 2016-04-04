#!/bin/bash

source ./config.sh

curl -H "Accept: application/json; indent=4" -u $AUTH -X GET $HOST/api/service/exampleservice/
