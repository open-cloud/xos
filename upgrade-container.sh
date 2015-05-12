#!/bin/bash

TMPDIR="/tmp/initdata"
XOSDIR="/home/ubuntu/xos"

mkdir -p $TMPDIR
rm -f $TMPDIR/*.json

XOS=$( docker ps|grep "xos:latest"|awk '{print $NF}' )
docker exec $XOS /opt/xos/scripts/opencloud dumpdata
docker cp $XOS:/opt/xos_backups/dumpdata-latest.json $TMPDIR
docker cp $XOS:/opt/xos/xos_config $TMPDIR
cp $TMPDIR/*.json $XOSDIR/xos/core/fixtures/initial_data.json
cp $TMPDIR/xos_config $XOSDIR/xos/

git pull

if [[ $? != 0 ]]; then
    echo "git pull" failed
    exit
fi

docker build -t xos .

docker stop $XOS
docker run -p 8000:8000 xos 
