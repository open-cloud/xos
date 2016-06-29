source ../../setup/admin-openrc.sh

get_ip () {
    LABEL=$1
    NETWORK=$2
    nova list --all-tenants|grep $LABEL|sed "s/^.*$NETWORK=//g"|sed 's/; .*$//g'|awk '{print $1}'
    }

GRENAMES=()
BM_IPS=()

NODES=`sudo bash -c "source ../../setup/admin-openrc.sh ; nova hypervisor-list" |grep enabled|awk '{print $4}'`
I=1
for NODE in $NODES; do
    BM_SSH_IP=`getent hosts $NODE | awk '{ print $1 }'`
    IFS=. read BM_NAME BM_REMAINDER <<< $NODE
    BM_IP=`sudo grep -i $BM_NAME /root/setup/data-hosts.flat-lan-1 | awk '{print $1}'`

    GRE_NAMES+=("gre-bm-$I")
    BM_IPS+=("$BM_IP")

    #echo switch_volt$I    ansible_ssh_host=$( get_ip mysite_volt flat-lan-1-net) grename=gre-bm-$I bm_addr=$BM_IP
    echo bm$I           ansible_ssh_host=$BM_SSH_IP grename=gre-bm-$I volt_addr=$( get_ip mysite_volt flat-lan-1-net)  ansible_ssh_private_key_file=/root/.ssh/id_rsa
    I=$(( I+1 ))
done

GRE_NAMES=${GRE_NAMES[@]}
BM_IPS=${BM_IPS[@]}

echo switch_volt ansible_ssh_host=$( get_ip mysite_volt flat-lan-1-net) grenames=\"$GRE_NAMES\" bm_ips=\"$BM_IPS\"

NM=`grep "^nm" /root/setup/fqdn.map | awk '{ print $2 }'`
echo "nm1 ansible_ssh_host=$NM ansible_ssh_private_key_file=/root/.ssh/id_rsa"

echo "[baremetal]"
I=1
for NODE in $NODES; do
    echo bm$I
    I=$((I+1))
done

# now for the network management node
echo "[nm]"
echo "nm1"
