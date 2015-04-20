#!/bin/bash

HOST=198.0.0.44:8000
AUTH=scott@onlab.us:letmein
ID=974

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X DELETE $HOST/xoslib/volttenant/$ID/  