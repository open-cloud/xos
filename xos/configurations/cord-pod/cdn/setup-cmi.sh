#! /bin/bash

source cmi-settings.sh

#apt-get -y install sshpass

echo "[ssh_connection]" > cmi.conf
echo "ssh_args = -o \"ProxyCommand ssh -q -i $NODE_KEY -o StrictHostKeyChecking=no root@$COMPUTE_NODE nc $MGMT_IP 22\"" >> cmi.conf
echo "scp_if_ssh = True" >> cmi.conf
echo "pipelining = True" >> cmi.conf
echo >> cmi.conf
echo "[defaults]" >> cmi.conf
echo "host_key_checking = False" >> cmi.conf

echo "cmi ansible_ssh_private_key_file=$VM_KEY" > cmi.hosts

export ANSIBLE_CONFIG=cmi.conf
export ANSIBLE_HOSTS=cmi.hosts

ansible-playbook -v cmi.yaml
