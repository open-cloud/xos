#!/bin/sh

TMPDIR="/tmp/initdata"
XOSDIR="/home/ubuntu/xos"

mkdir -p $TMPDIR
rm -f $TMPDIR/*.json

XOS=$( docker ps|grep "xos:latest"|awk '{print $NF}' )
docker exec $XOS /opt/xos/scripts/opencloud dumpdata
docker cp $XOS:/opt/xos_backups/dumpdata-latest.json $TMPDIR
cp $TMPDIR/*.json $XOSDIR/xos/core/fixtures/initial_data.json

git pull
docker build -t xos .

docker stop $XOS
docker run -p 8000:8000 xos 
