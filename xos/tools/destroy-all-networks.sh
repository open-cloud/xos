#! /bin/bash

# This will destroy all neutron networks, routers, and ports on Cloudlab. 
# It even destroys ext-net, flat-net, and tun-net
# Don't use it unless you really want that to happen.

source /root/setup/admin-openrc.sh

echo "Lots of stuff will fail -- don't worry about it"

PORTS=`neutron port-list | grep -v "+----" | grep -v "mac_address" | awk '{print $2}'`
for PORT in $PORTS; do
   echo "Deleting port $PORT"
   neutron port-delete $PORT
done

NET_SUBNETS=`neutron net-list | grep -v "+----" | grep -v "subnets" | awk '{print $6}'`
ROUTERS=`neutron router-list | grep -v "+----" | grep -v "external_gateway_info" | awk '{print $2}'`  

for ROUTER in $ROUTERS; do
for SUBNET in $NET_SUBNETS; do
neutron router-interface-delete $ROUTER $SUBNET
done
neutron router-delete $ROUTER
done

echo "Stuff below this line shouldn't fail"

NETS=`neutron net-list | grep -v "+----" | grep -v "subnets" | awk '{print $2}'`  
for NET in $NETS; do
   echo "Deleting network"
   neutron net-delete $NET
done
   