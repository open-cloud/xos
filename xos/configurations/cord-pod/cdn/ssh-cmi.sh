#! /bin/bash

source ./cmi-settings.sh

ssh -i $VM_KEY -o "ProxyCommand ssh -q -i $NODE_KEY -o StrictHostKeyChecking=no root@$COMPUTE_NODE nc $MGMT_IP 22" root@cmi
