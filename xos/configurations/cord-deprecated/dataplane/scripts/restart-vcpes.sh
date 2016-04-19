#!/bin/sh

for VCPE in $( docker ps|grep vcpe|awk '{print $NF}' )
do
  service $VCPE stop
  sleep 1
  service $VCPE start
done
