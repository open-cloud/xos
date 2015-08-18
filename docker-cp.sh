#! /bin/bash                                                                                                             
# script for copying stuff into running Docker container
# usage: docker-cp.sh <src> <dest>
# example: docker-cp.sh foo /tmp/foo

XOS=$( docker ps|grep "xos"|awk '{print $NF}' )
FOLDER=`docker inspect -f   '{{.Id}}' $XOS`
cp $1 /var/lib/docker/aufs/mnt/$FOLDER/$2