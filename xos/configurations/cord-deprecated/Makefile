SETUPDIR:=../setup
MYIP:=$(shell hostname -i)

cloudlab: common_cloudlab cord acord

devstack: upgrade_pkgs common_devstack devstack_net_fix cord

cord: virtualbng_json vtn_network_cfg_json
	sudo MYIP=$(MYIP) docker-compose up -d
	bash ../common/wait_for_xos.sh
	sudo MYIP=$(MYIP) docker-compose run xos python /opt/xos/tosca/run.py none /opt/xos/configurations/common/fixtures.yaml
	sudo docker-compose run xos python /opt/xos/tosca/run.py none /opt/xos/configurations/common/mydeployment.yaml
	sudo MYIP=$(MYIP) docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/common/cloudlab-openstack.yaml
	sudo MYIP=$(MYIP) docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /root/setup/nodes.yaml
	sudo MYIP=$(MYIP) docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/cord/cord.yaml

containers:
	cd ../../../containers/xos; make devel
	cd ../../../containers/synchronizer; make

common_cloudlab:
	make -C ../common -f Makefile.cloudlab

common_devstack:
	make -C ../common -f Makefile.devstack

acord: cloudlab_ceilometer_custom_images ceilometer_cloudlab_cord_plugins
	sudo MYIP=$(MYIP) docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/cord/ceilometer.yaml

ceilometer_cloudlab_cord_plugins:
	if [ -d ./ceilometer-plugins ]; then rm -fr ./ceilometer-plugins; fi
	git clone https://github.com/srikanthvavila/ceilometer-plugins.git
	sudo cp -r ceilometer-plugins/network/ext_services /usr/lib/python2.7/dist-packages/ceilometer/network/
	sudo cp -r ceilometer-plugins/network/statistics/onos /usr/lib/python2.7/dist-packages/ceilometer/network/statistics/
	sudo cp ceilometer-plugins/network/statistics/__init__.py /usr/lib/python2.7/dist-packages/ceilometer/network/statistics/ 
	sudo cp ceilometer-plugins/entry_points.txt /usr/lib/python2.7/dist-packages/ceilometer-*egg-info/
	sudo cp ceilometer-plugins/pipeline.yaml /etc/ceilometer/
	echo "Restarting ceilometer-agent-notification"
	sudo service ceilometer-agent-notification restart
	echo "Restarting ceilometer-agent-central"
	sudo service ceilometer-agent-central restart

ceilometer_pub_sub:
	if [ -d ./pub-sub ]; then rm -fr ./pub-sub; fi
	git clone https://github.com/srikanthvavila/pub-sub.git
	echo "Starting Ceilometer PUB/SUB service...Ensure zookeeper and kafka services are launched (if required)"
	cd pub-sub/ceilometer_pub_sub/ ; python sub_main.py & 
	cd ../..

virtualbng_json:
	export SETUPDIR=$(SETUPDIR); bash make-virtualbng-json.sh

vtn_network_cfg_json:
	export SETUPDIR=$(SETUPDIR); bash make-vtn-networkconfig-json.sh

stop:
	sudo MYIP=$(MYIP) docker-compose stop

rm:
	sudo MYIP=$(MYIP) docker-compose rm

showlogs:
	sudo MYIP=$(MYIP) docker-compose logs

ps:
	sudo MYIP=$(MYIP) docker-compose ps

dataplane: etc_hosts
	cd dataplane; ./gen-inventory.sh > hosts
	cd dataplane; ansible-playbook -i hosts dataplane.yaml

dataplane_bm: dataplane
	cd dataplane; bash -c "./generate-bm.sh > hosts-bm"
	cd dataplane; sudo bash -c "ansible-playbook -i hosts-bm dataplane-bm.yaml"

etc_hosts:
	sudo bash -c "sed -i '/^10.11.10/ d' /etc/hosts"
	cd dataplane; sudo bash -c "./gen-etc-hosts.sh >> /etc/hosts"

setup_client:
	# add subscriber to vOLT?  Is there a REST API?
	echo "Don't forget: add-subscriber-access of:0000000000000001 1 432"
	cd dataplane; ansible -i hosts client -m shell -s -a "route del default gw 10.11.10.5; dhclient br-sub"
	# reboot the vBNG ONOS
	cd dataplane; ansible -i hosts onos_vbng -m shell -s -a "docker restart ONOS"

cleanup: stop rm
	cd dataplane; ./cleanup.sh
	bash -c "source ../setup/admin-openrc.sh; nova list --all-tenants; neutron net-list"
	echo "Don't forget to clean up vCPE containers"

devstack_net_fix:
	sudo ../common/devstack/net-fix.sh
	sudo bash -c "source ../setup/admin-openrc.sh; neutron subnet-update private-subnet --dns-nameservers list=true 8.8.8.8 8.8.4.4"

upgrade_pkgs:
	sudo pip install httpie --upgrade

cloudlab_ceilometer_custom_images:
	bash -c "source ../setup/admin-openrc.sh; glance image-show ceilometer-trusty-server-multi-nic || if test -f /proj/xos-PG0/images/ceilometer-trusty-server-multi-nic.compressed.qcow2 ; then glance image-create --name ceilometer-trusty-server-multi-nic --disk-format qcow2 --file /proj/xos-PG0/images/ceilometer-trusty-server-multi-nic.compressed.qcow2 --container-format bare ; else mkdir -p /tmp/images && wget http://www.vicci.org/cord/ceilometer-trusty-server-multi-nic.compressed.qcow2 -P /tmp/images && glance image-create --name ceilometer-trusty-server-multi-nic --disk-format qcow2 --file /tmp/images/ceilometer-trusty-server-multi-nic.compressed.qcow2 --container-format bare ; fi "
