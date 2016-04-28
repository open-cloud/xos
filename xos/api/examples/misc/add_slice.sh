#!/bin/bash

source ./config.sh

SITE_ID=1
USER_ID=1

DATA=$(cat <<EOF
{"name": "mysite_test1",
 "site": $SITE_ID,
 "creator": $USER_ID
}
EOF
)

curl -H "Accept: application/json; indent=4" -H "Content-Type: application/json" -u $AUTH -X POST -d "$DATA" $HOST/xos/slices/?no_hyperlinks=1
