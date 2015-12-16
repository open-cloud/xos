FN=vtn-network-cfg.json

rm -f $FN

cat >> $FN <<EOF
{
    "apps" : {
        "org.onosproject.cordvtn" : {
            "cordvtn" : {
                "nodes" : [
EOF

NODES=$( sudo bash -c "source /root/setup/admin-openrc.sh ; nova hypervisor-list" |grep cloudlab|awk '{print $4}' )

NODECOUNT=0
for NODE in $NODES; do
    ((NODECOUNT++))
done

I=0
for NODE in $NODES; do
    echo $NODE
    NODEIP=`getent hosts $NODE | awk '{ print $1 }'`

    ((I++))
    cat >> $FN <<EOF
                    {
                      "hostname": "$NODE",
                      "ovsdbIp": "$NODEIP",
                      "ovsdbPort": "6640",
                      "bridgeId": "of:000000000000000$I"
EOF
    if [[ "$I" -lt "$NODECOUNT" ]]; then
        echo "                    }," >> $FN
    else
        echo "                    }" >> $FN
    fi
done

NEUTRONIP="127.0.0.1"
KEYSTONEIP="127.0.0.1"

cat >> $FN <<EOF
                ]
            }
        },
        "org.onosproject.openstackswitching" : {
            "openstackswitching" : {
                 "do_not_push_flows" : "true",
                 "neutron_server" : "http://$NEUTRONIP:9696/v2.0/",
                 "keystone_server" : "http://$KEYSTONEIP:5000/v2.0/",
                 "user_name" : "admin",
                 "password" : "passwd"
             }
        }
    }
}
EOF
