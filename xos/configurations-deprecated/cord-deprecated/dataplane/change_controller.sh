#! /bin/bash

# put IP address of node running ONOS VTN App here
DESIRED_CONTROLLER="tcp:130.127.133.24:6653"

while [[ 1 ]]; do
    CONTROLLER=`ovs-vsctl get-controller br-int`
    if [[ "$CONTROLLER" == "tcp:172.17.0.2:6653" ]]; then
       ovs-vsctl set-controller br-int $DESIRED_CONTROLLER
       echo "changed controller from $CONTROLLER to $DESIRED_CONTROLLER"
    fi
    sleep 10s
done
