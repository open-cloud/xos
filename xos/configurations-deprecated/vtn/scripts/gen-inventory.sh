FN=/etc/ansible/hosts

echo "Writing to $FN"

rm -f $FN

cat >> $FN <<EOF
localhost

[nodes]
EOF

NODES=$( sudo bash -c "source $SETUPDIR/admin-openrc.sh ; nova hypervisor-list" |grep enabled|awk '{print $4}' )

# also configure ONOS to manage the nm node
NM=`grep "^nm" /root/setup/fqdn.map | awk '{ print $2 }'`
NODES="$NODES $NM"

for NODE in $NODES; do
    cat >> $FN <<EOF
$NODE
EOF
done

cat >> $FN <<EOF
[nodes:vars]
ansible_ssh_user=root
ansible_ssh_key=/root/setup/id_rsa
EOF
