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
NM=`grep "^nm" /root/setup/fqdn.map | awk '{ print $2 }'`
NODES="$NODES $NM"

NODECOUNT=0
for NODE in $NODES; do
    ((NODECOUNT++))
done

I=0
for NODE in $NODES; do
    echo $NODE
    NODEIP=`getent hosts $NODE | awk '{ print $1 }'`

    # This part is cloudlab-specific. It examines the flat-net-1 network and extracts
    # the eth device and ip address that was assigned to flat-net-1.
    sudo scp root@$NODE:/root/setup/info.flat-lan-1 $SETUPDIR/flat-lan-$NODE
    PHYPORT=`bash -c "source $SETUPDIR/flat-lan-$NODE; echo \\\$DATADEV"`
    LOCALIP=`bash -c "source $SETUPDIR/flat-lan-$NODE; echo \\\$DATAIP"`

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

HOSTNAME=`hostname`
NEUTRONIP=`getent hosts $HOSTNAME | awk '{ print $1 }'`
KEYSTONEIP=`getent hosts $HOSTNAME | awk '{ print $1 }'`

cat >> $FN <<EOF
                ]
            }
        },
        "org.onosproject.openstackswitching" : {
            "openstackswitching" : {
                 "do_not_push_flows" : "true",
                 "neutron_server" : "http://$NEUTRONIP:9696/v2.0/",
                 "keystone_server" : "http://$KEYSTONEIP:5000/v2.0/",
                 "user_name" : "$OS_USERNAME",
                 "password" : "$OS_PASSWORD"
             }
        }
    }
}
EOF
