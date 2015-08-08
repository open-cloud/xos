#!/bin/bash
set -x

# This script assumes that it is being run on the ctl node of the Tutorial-OpenStack
# profile on CloudLab.

XOS="http://ctl:9999/"
AUTH="padmin@vicci.org:letmein"

# Install Docker
wget -qO- https://get.docker.com/ | sh
sudo usermod -aG docker $(whoami)

sudo apt-get install httpie

sudo docker build -t xos .

# OpenStack is using port 8000...
MYIP=$( hostname -i )
sudo docker run -d --add-host="ctl:$MYIP" -p 9999:8000 xos

echo "Waiting for XOS to come up"
until http $XOS &> /dev/null
do
    sleep 1
done

# Create public key if none present
cat /dev/zero | ssh-keygen -q -N ""
PUBKEY=$( cat ~/.ssh/id_rsa.pub )

# Copy public key
# BUG: Shouldn't have to set the 'enacted' field...
http --auth $AUTH PATCH $XOS/xos/users/1/ public_key="$PUBKEY" enacted=$( date "+%Y-%m-%dT%T")

# Set up controller
http --auth $AUTH POST $XOS/xos/controllers/ name=CloudLab deployment=$XOS/xos/deployments/1/ backend_type=OpenStack version=Juno auth_url="http://ctl:5000/v2.0" admin_user=admin admin_tenant=admin admin_password="N!ceD3m0"

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
