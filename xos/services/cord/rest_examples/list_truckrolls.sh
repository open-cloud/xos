#!/bin/bash

source ./config.sh

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH $HOST/xoslib/truckroll/  
