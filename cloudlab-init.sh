#!/bin/sh

# This script assumes that XOS is running in a Docker container on the local machine,
# using an image called 'xos'.

# CHANGE THE FOLLOWING FOR YOUR CLOUDLAB INSTALLATION
# URL for your XOS installation
XOS="http://192.168.59.103:8000/"
# The IP address of the OpenStack head node on CloudLab
CTL_IP="128.104.222.18"
# The DNS name of the OpenStack compute node, as shown by 'nova hypervisor-list'
NODE="cp1.acb-qv7993.planetcloud-pg0.wisc.cloudlab.us"
# The public key that you want to use to login to instances
PUBKEY="ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEArlgZWcRP75W2/e5bKG1FEeec1OJQuw9dGVyo3TdUgVu4F0/JgBsgR2BrTuQ+mzm+N47ZkSrYwLdAJGuvL7ECxc6aouQ6AtQ/biU1gsrfuPnnUBjfAGqlP/L77lYxpLAPglx/HCCBu53gLKVt8lRDyyGZaWnB7fGlnwrn5AMjcfXsz5Ia8W6oBmxy2fxDSR9SpTs5yAzfcj37mCBtOZBwdjb54B36WpFq9BwFrEXxbvxH4aU0WSneJagicZuCUXnTg2YSURBD0jBmTrYOVRfTZzNPyagOvuIhnnakOSGkGa8s4SrC5zymZsVPdQbp6icRsu6OjKZ83Y0oiTQ4rTaeUw== acb@cadenza.cs.princeton.edu"
# END CHANGES

AUTH="padmin@vicci.org:letmein"
CONTAINER=$( docker ps|grep xos|awk '{print $(NF)}' )

# Copy public key
# BUG: Shouldn't have to set the 'enacted' field...
http --auth $AUTH PATCH $XOS/xos/users/1/ public_key="$PUBKEY" enacted=$( date "+%Y-%m-%dT%T")

# Fix /etc/hosts, necessary for OpenStack endpoints
docker exec $CONTAINER bash -c "echo $CTL_IP ctl >> /etc/hosts"

# Set up controller
http --auth $AUTH POST $XOS/xos/controllers/ name=CloudLab deployment=$XOS/xos/deployments/1/ backend_type=OpenStack version=Juno auth_url="http://ctl:5000/v2.0" admin_user=admin admin_tenant=admin admin_password="N!ceD3m0"

# Add controller to site
http --auth $AUTH PATCH $XOS/xos/sitedeployments/1/ controller=$XOS/xos/controllers/1/

# Add image
http --auth $AUTH POST $XOS/xos/images/ name=trusty-server-multi-nic disk_format=QCOW2 container_format=BARE

# Activate image
http --auth $AUTH POST $XOS/xos/imagedeploymentses/ deployment=$XOS/xos/deployments/1/ image=$XOS/xos/images/1/

# Add node
http --auth $AUTH POST $XOS/xos/nodes/ name=$NODE site_deployment=$XOS/xos/sitedeployments/1/

# Modify networktemplate/2
# BUG: Shouldn't have to set the controller_kind field, it's invalid in the initial fixture
http --auth $AUTH PATCH $XOS/xos/networktemplates/2/ shared_network_name=tun-data-net controller_kind=""
