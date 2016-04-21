#!/bin/bash

# If running on a CloudLab node, set up extra disk space
if [ -e /usr/testbed/bin/mkextrafs ]
then
    sudo mkdir -p /opt/stack
    sudo /usr/testbed/bin/mkextrafs -f /opt/stack
fi

cd ~
git clone https://github.com/open-cloud/xos.git
git clone https://git.openstack.org/openstack-dev/devstack
cd ~/devstack
git checkout stable/kilo
cp ~/xos/xos/configurations/common/devstack/local.conf .
./stack.sh
