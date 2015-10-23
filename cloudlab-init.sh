#!/bin/bash
set -x

# This script assumes that it is being run on the ctl node of the OpenStack
# profile on CloudLab.

XOS="http://ctl:9999/"
AUTH="padmin@vicci.org:letmein"
CORD=0
IMAGE="xos"

# Create public key if none present
[ -e ~/.ssh/id_rsa ] || cat /dev/zero | ssh-keygen -q -N ""

# Install Docker
which docker > /dev/null || wget -qO- https://get.docker.com/ | sh
sudo usermod -aG docker $(whoami)

sudo apt-get -y install httpie

if [ "$CORD" -ne 0 ]
then
    cp ~/.ssh/id_rsa.pub xos/observers/vcpe/vcpe_public_key
    cp ~/.ssh/id_rsa     xos/observers/vcpe/vcpe_private_key
    cp ~/.ssh/id_rsa.pub xos/observers/monitoring_channel/monitoring_channel_public_key
    cp ~/.ssh/id_rsa     xos/observers/monitoring_channel/monitoring_channel_private_key
fi

sudo docker build -t xos .

if [ "$CORD" -ne 0 ]
then
    sudo docker build -t cord -f Dockerfile.cord .
    IMAGE="cord"
fi

# OpenStack is using port 8000...
MYIP=$( hostname -i )
MYFLATLANIF=$( sudo bash -c "netstat -i" |grep flat|awk '{print $1}' )
MYFLATLANIP=$( ifconfig $MYFLATLANIF | grep "inet addr" | awk -F: '{print $2}' | awk '{print $1}' )
sudo docker run -d --add-host="ctl:$MYIP" -p 9999:8000 $IMAGE

echo "Waiting for XOS to come up"
until http $XOS &> /dev/null
do
    sleep 1
done

# Copy public key
# BUG: Shouldn't have to set the 'enacted' field...
PUBKEY=$( cat ~/.ssh/id_rsa.pub )
http --auth $AUTH PATCH $XOS/xos/users/1/ public_key="$PUBKEY" enacted=$( date "+%Y-%m-%dT%T")

# Set up controller
sudo cp /root/setup/admin-openrc.sh /tmp
sudo chmod a+r /tmp/admin-openrc.sh
#sudo sed -i 's/:5000/:35357/' /tmp/admin-openrc.sh
source /tmp/admin-openrc.sh

if [ "$CORD" -ne 1 ]
then
     http --auth $AUTH POST $XOS/xos/controllers/ name=CloudLab deployment=$XOS/xos/deployments/1/ backend_type=OpenStack version=Kilo auth_url=$OS_AUTH_URL admin_user=$OS_USERNAME admin_tenant=$OS_TENANT_NAME admin_password=$OS_PASSWORD domain=Default
else
     sudo cp /root/setup/settings /tmp
     sudo chmod a+r /tmp/settings
     source /tmp/settings
     source /tmp/admin-openrc.sh
     http --auth $AUTH POST $XOS/xos/controllers/ name=CloudLab deployment=$XOS/xos/deployments/1/ backend_type=OpenStack version=Kilo auth_url=$OS_AUTH_URL admin_user=$OS_USERNAME admin_tenant=$OS_TENANT_NAME admin_password=$OS_PASSWORD domain=Default rabbit_host=$MYFLATLANIP rabbit_user=$RABBIT_USER rabbit_password=$RABBIT_PASS
fi

# Add controller to site
http --auth $AUTH PATCH $XOS/xos/sitedeployments/1/ controller=$XOS/xos/controllers/1/

# Add image
http --auth $AUTH POST $XOS/xos/images/ name=trusty-server-multi-nic disk_format=QCOW2 container_format=BARE

# Activate image
http --auth $AUTH POST $XOS/xos/imagedeploymentses/ deployment=$XOS/xos/deployments/1/ image=$XOS/xos/images/1/

# Add node
NODES=$( sudo bash -c "source /root/setup/admin-openrc.sh ; nova hypervisor-list" |grep cloudlab|awk '{print $4}' )
for NODE in $NODES
do
    http --auth $AUTH POST $XOS/xos/nodes/ name=$NODE site_deployment=$XOS/xos/sitedeployments/1/
done

# Modify networktemplate/2
# BUG: Shouldn't have to set the controller_kind field, it's invalid in the initial fixture
FLATNET=$( sudo bash -c "source /root/setup/admin-openrc.sh ; neutron net-list" |grep flat|awk '{print $4}' )
http --auth $AUTH PATCH $XOS/xos/networktemplates/2/ shared_network_name=$FLATNET controller_kind=""

if [ "$CORD" -ne 0 ]
then
    DOCKER=$( sudo docker ps|grep $IMAGE|awk '{print $NF}' )
    sudo docker exec $DOCKER bash -c "cd /opt/xos/tosca; python run.py padmin@vicci.org samples/cord-cloudlab.yaml; python run.py padmin@vicci.org samples/ceilometer.yaml"
fi
