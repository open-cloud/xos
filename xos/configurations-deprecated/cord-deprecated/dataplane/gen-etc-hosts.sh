#!/bin/bash
# set -x

source ../../setup/admin-openrc.sh

get_ip () {
    LABEL=$1
    NETWORK=$2
    nova list --all-tenants|grep $LABEL|sed "s/^.*$NETWORK=//g"|sed 's/; .*$//g'|awk '{print $1}'
}

cat <<EOF
$( get_ip mysite_onos_vbng flat-lan-1-net) onos_vbng
$( get_ip mysite_vbng flat-lan-1-net) switch_vbng
$( get_ip mysite_onos_volt flat-lan-1-net) onos_volt
$( get_ip mysite_volt flat-lan-1-net) switch_volt
$( get_ip mysite_clients flat-lan-1-net) client
$( get_ip mysite_vsg flat-lan-1-net) vcpe
EOF
