#! /bin/bash

export SETUPDIR=/root/setup

# copy in file necessary to setup VTN

cd ../cord
CONTAINER=$( docker ps|grep "xos"|awk '{print $NF}' )
make vtn_network_cfg_json
docker cp $SETUPDIR/vtn-network-cfg.json $CONTAINER:/root/setup/
docker cp ../common/id_rsa.pub $CONTAINER:/opt/xos/observers/onos/onos_key.pub
docker cp ../common/id_rsa $CONTAINER:/opt/xos/observers/onos/onos_key
