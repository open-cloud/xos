source ~/admin-openrc.sh

get_ip () {
    LABEL=$1
    NETWORK=$2
    nova list --all-tenants|grep $LABEL|sed "s/^.*$NETWORK=//g"|sed 's/; .*$//g'|awk '{print $1}'
    }

NODES=`sudo bash -c "source /root/setup/admin-openrc.sh ; nova hypervisor-list" |grep cloudlab|awk '{print $4}'`
I=1
for NODE in $NODES; do
    IP=`getent hosts $NODE | awk '{ print $1 }'`
    echo switch_volt$I    ansible_ssh_host=$( get_ip mysite_volt flat-lan-1-net) grename=gre-bm-$I bm_addr=$IP
    echo bm$I           ansible_ssh_host=$IP grename=gre-bm-$I volt_addr=$( get_ip mysite_volt lan_network)  ansible_ssh_private_key_file=/root/.ssh/id_rsa
    I=$(( I+1 ))
done

# a kludge for now -- just rerun the onos_volt step for each baremetal machine

echo "[switch_volt]"
I=1
for NODE in $NODES; do
    echo switch_volt$I
    I=$((I+1))
done

echo "[baremetal]"
I=1
for NODE in $NODES; do
    echo bm$I
    I=$((I+1))
done
