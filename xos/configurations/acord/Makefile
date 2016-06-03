SETUPDIR:=../setup
MYIP:=$(shell hostname -i)

cloudlab: common_cloudlab cloudlab_ceilometer_custom_images ceilometer_cloudlab_cord_plugins acord

devstack: upgrade_pkgs common_devstack devstack_net_fix devstack_images ceilometer_devstack_cord_plugins acord

cord: 
	sudo MYIP=$(MYIP) docker-compose up -d
	bash ../common/wait_for_xos.sh
	sudo MYIP=$(MYIP) docker-compose run xos python /opt/xos/tosca/run.py none /opt/xos/configurations/common/fixtures.yaml
	sudo docker-compose run xos python /opt/xos/tosca/run.py none /opt/xos/configurations/common/mydeployment.yaml
	sudo MYIP=$(MYIP) docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/common/cloudlab-openstack.yaml
	sudo MYIP=$(MYIP) docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /root/setup/nodes.yaml

acord: cord exampleservice
	sudo MYIP=$(MYIP) docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/acord/ceilometer.yaml

exampleservice:
	#Ensure exampleservice is enabled in xos/tools/xos-manage and xos/settings.py file before uncommenting below lines
	#sudo docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/acord/acord-exampleservice.yaml

containers:
	cd ../../../containers/xos; make devel
	cd ../../../containers/synchronizer; make

common_cloudlab:
	make -C ../common -f Makefile.cloudlab

common_devstack:
	make -C ../common -f Makefile.devstack

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

ceilometer_devstack_cord_plugins:
	if [ -d ./ceilometer-plugins ]; then rm -fr ./ceilometer-plugins; fi
	git clone https://github.com/srikanthvavila/ceilometer-plugins.git
	sudo cp -r ceilometer-plugins/network/ext_services /opt/stack/ceilometer/ceilometer/network/
	sudo cp ceilometer-plugins/entry_points.txt /opt/stack/ceilometer/ceilometer*egg-info/
	sudo cp ceilometer-plugins/pipeline.yaml /etc/ceilometer/
	echo "Remember to restart ceilometer-anotification ceilometer-acentral screens"

ceilometer_pub_sub:
	if [ -d ./pub-sub ]; then rm -fr ./pub-sub; fi
	git clone https://github.com/srikanthvavila/pub-sub.git
	echo "Starting Ceilometer PUB/SUB service...Ensure zookeeper and kafka services are launched (if required)"
	cd pub-sub/ceilometer_pub_sub/ ; python sub_main.py & 
	cd ../..

stop:
	sudo MYIP=$(MYIP) docker-compose stop

rm: stop
	sudo MYIP=$(MYIP) docker-compose rm

showlogs:
	sudo MYIP=$(MYIP) docker-compose logs

ps:
	sudo MYIP=$(MYIP) docker-compose ps

cleanup: stop rm
	./cleanup.sh
	bash -c "source ../setup/admin-openrc.sh; nova list --all-tenants; neutron net-list"

devstack_net_fix:
	sudo ../common/devstack/net-fix.sh
	sudo bash -c "source ../setup/admin-openrc.sh; neutron subnet-update private-subnet --dns-nameservers list=true 8.8.8.8 8.8.4.4"

upgrade_pkgs:
	sudo pip install httpie --upgrade

rebuild_xos:
	make -C ../../../containers/xos devel

rebuild_synchronizer:
	make -C ../../../containers/synchronizer

devstack_images:
	bash -c "source ../setup/admin-openrc.sh; glance image-show ceilometer-trusty-server-multi-nic || ! mkdir -p /opt/stack/images || ! wget http://www.vicci.org/cord/ceilometer-trusty-server-multi-nic.compressed.qcow2 -P /opt/stack/images || glance image-create --name ceilometer-trusty-server-multi-nic --disk-format qcow2 --file /opt/stack/images/ceilometer-trusty-server-multi-nic.compressed.qcow2 --container-format bare"

cloudlab_ceilometer_custom_images:
	bash -c "source ../setup/admin-openrc.sh; glance image-show ceilometer-trusty-server-multi-nic || if test -f /proj/xos-PG0/images/ceilometer-trusty-server-multi-nic.compressed.qcow2 ; then glance image-create --name ceilometer-trusty-server-multi-nic --disk-format qcow2 --file /proj/xos-PG0/images/ceilometer-trusty-server-multi-nic.compressed.qcow2 --container-format bare ; else mkdir -p /tmp/images && wget http://www.vicci.org/cord/ceilometer-trusty-server-multi-nic.compressed.qcow2 -P /tmp/images && glance image-create --name ceilometer-trusty-server-multi-nic --disk-format qcow2 --file /tmp/images/ceilometer-trusty-server-multi-nic.compressed.qcow2 --container-format bare ; fi "
