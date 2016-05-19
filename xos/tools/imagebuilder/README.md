Prerequisites:

mkdir /image
curl http://www.vicci.org/cord/ceilometer-trusty-server-multi-nic.compressed.qcow2 > /image/trusty-server-multi-nic.img
apt-add-repository ppa:ansible/ansible
apt-get update
apt-get install ansible qemu-utils
modprobe nbd
