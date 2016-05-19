Prerequisites:

mkdir /image
curl http://www.vicci.org/cord/ceilometer-trusty-server-multi-nic.compressed.qcow2 > /image/trusty-server-multi-nic.img
apt-get install ansible qemu-utils
modprobe nbd
