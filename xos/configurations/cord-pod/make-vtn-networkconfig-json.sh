FN=$SETUPDIR/vtn-network-cfg.json

echo "Writing to $FN"

rm -f $FN

cat >> $FN <<EOF
{
    "apps" : {
        "org.onosproject.cordvtn" : {
            "cordvtn" : {
                "gatewayMac" : "00:00:00:00:00:01",
                "nodes" : [
EOF

NODES=$( sudo bash -c "source $SETUPDIR/admin-openrc.sh ; nova hypervisor-list" |grep -v ID|grep -v +|awk '{print $4}' )

# also configure ONOS to manage the nm node
NM="neutron-gateway"
NODES="$NODES $NM"

NODECOUNT=0
for NODE in $NODES; do
    ((NODECOUNT++))
done

I=0
for NODE in $NODES; do
    echo $NODE
    NODEIP=`getent hosts $NODE | awk '{ print $1 }'`

    PHYPORT=eth0
    LOCALIP=$NODEIP

    ((I++))
    cat >> $FN <<EOF
                    {
                      "hostname": "$NODE",
                      "ovsdbIp": "$NODEIP",
                      "ovsdbPort": "6641",
                      "bridgeId": "of:000000000000000$I",
                      "phyPortName": "$PHYPORT",
                      "localIp": "$LOCALIP"
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
        "org.onosproject.openstackswitching" : {
            "openstackswitching" : {
                 "do_not_push_flows" : "true",
                 "neutron_server" : "$NEUTRON_URL/v2.0/",
                 "keystone_server" : "$OS_AUTH_URL",
                 "user_name" : "$OS_USERNAME",
                 "password" : "$OS_PASSWORD"
             }
        }
    }
}
EOF
