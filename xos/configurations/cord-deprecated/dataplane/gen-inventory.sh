#!/bin/bash
# set -x

source ../../setup/admin-openrc.sh

get_ip () {
    LABEL=$1
    NETWORK=$2
    nova list --all-tenants|grep $LABEL|sed "s/^.*$NETWORK=//g"|sed 's/; .*$//g'|awk '{print $1}'
}

cat <<EOF
onos_vbng    ansible_ssh_host=$( get_ip mysite_onos_vbng flat-lan-1-net)
switch_vbng  ansible_ssh_host=$( get_ip mysite_vbng flat-lan-1-net) wan_ip=$( get_ip mysite_vbng wan_network) public_ip=$( get_ip mysite_vbng tun0-net )

onos_volt    ansible_ssh_host=$( get_ip mysite_onos_volt flat-lan-1-net)
switch_volt  ansible_ssh_host=$( get_ip mysite_volt flat-lan-1-net) subscriber_ip=$( get_ip mysite_volt subscriber_network) lan_ip=$( get_ip mysite_volt lan_network)

client       ansible_ssh_host=$( get_ip mysite_clients flat-lan-1-net) subscriber_ip=$( get_ip mysite_clients subscriber_network)
vcpe         ansible_ssh_host=$( get_ip mysite_vsg flat-lan-1-net) lan_ip=$( get_ip mysite_vsg lan_network)
EOF
