FN=$SETUPDIR/virtualbng.json

rm -f $FN

cat >> $FN <<EOF
{
    "localPublicIpPrefixes" : [
        "10.254.0.128/25"
    ],
    "nextHopIpAddress" : "10.254.0.1",
    "publicFacingMac" : "00:00:00:00:00:66",
    "xosIpAddress" : "10.11.10.1",
    "xosRestPort" : "9999",
    "hosts" : {
EOF

NODES=$( sudo bash -c "source $SETUPDIR/admin-openrc.sh ; nova hypervisor-list" |grep -v ID|grep -v +|awk '{print $4}' )

NODECOUNT=0
for NODE in $NODES; do
    ((NODECOUNT++))
done

I=0
for NODE in $NODES; do
    echo $NODE
    ((I++))
    if [[ "$I" -lt "$NODECOUNT" ]]; then
        echo "      \"$NODE\" : \"of:0000000000000001/1\"," >> $FN
    else
        echo "      \"$NODE\" : \"of:0000000000000001/1\"" >> $FN
    fi
done

cat >> $FN <<EOF
    }
}
EOF
