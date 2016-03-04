FN=$SETUPDIR/vtn-network-cfg.json

echo "Writing to $FN"

rm -f $FN

cat >> $FN <<EOF
{
    "apps" : {
        "org.onosproject.cordvtn" : {
            "cordvtn" : {
                "privateGatewayMac" : "00:00:00:00:00:01",
                "localManagementIp": "172.27.0.1/24",
                "ovsdbPort": "6641",
                "sshPort": "22",
                "sshUser": "root",
                "sshKeyFile": "/root/node_key",
                "publicGateways": [
                    {
                        "gatewayIp": "10.168.0.1",
                        "gatewayMac": "02:42:0a:a8:00:01"
                    }
                ],
                "nodes" : [
EOF

NODES=$( sudo bash -c "source $SETUPDIR/admin-openrc.sh ; nova hypervisor-list" |grep -v ID|grep -v +|awk '{print $4}' )

# XXX disabled - we don't need or want the nm node at this time
# also configure ONOS to manage the nm node
#NM="neutron-gateway"
#NODES="$NODES $NM"

NODECOUNT=0
for NODE in $NODES; do
    ((NODECOUNT++))
done

I=0
for NODE in $NODES; do
    echo $NODE
    NODEIP=`getent hosts $NODE | awk '{ print $1 }'`

    PHYPORT=veth1
    # How to set LOCALIP?
    LOCALIPNET="192.168.199"

    ((I++))
    cat >> $FN <<EOF
                    {
                      "hostname": "$NODE",
                      "hostManagementIp": "$NODEIP/24",
                      "bridgeId": "of:000000000000000$I",
                      "dataPlaneIntf": "$PHYPORT",
                      "dataPlaneIp": "$LOCALIPNET.$I/24"
EOF
    if [[ "$I" -lt "$NODECOUNT" ]]; then
        echo "                    }," >> $FN
    else
        echo "                    }" >> $FN
    fi
done

# get the openstack admin password and username
source $SETUPDIR/admin-openrc.sh
NEUTRON_URL=`keystone endpoint-get --service network|grep publicURL|awk '{print $4}'`

cat >> $FN <<EOF
                ]
            }
        },
        "org.onosproject.openstackinterface" : {
            "openstackinterface" : {
                 "do_not_push_flows" : "true",
                 "neutron_server" : "$NEUTRON_URL/v2.0/",
                 "keystone_server" : "$OS_AUTH_URL/",
                 "user_name" : "$OS_USERNAME",
                 "password" : "$OS_PASSWORD"
             }
        }
    }
}
EOF
