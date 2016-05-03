#!/bin/bash

source ./config.sh
source ./util.sh

curl -H "Accept: application/json; indent=4" -u $AUTH -X GET $HOST/api/utility/sshkeys/
