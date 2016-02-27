SETUPDIR:=../setup
MYIP:=$(shell hostname -i)

cloudlab: common_cloudlab acord

devstack: upgrade_pkgs common_devstack devstack_net_fix acord

acord: ceilometer_dashboard
	sudo MYIP=$(MYIP) docker-compose up -d
	bash ../common/wait_for_xos.sh
	sudo MYIP=$(MYIP) docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/common/fixtures.yaml
	sudo MYIP=$(MYIP) docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/common/base.yaml
	sudo MYIP=$(MYIP) docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /root/setup/nodes.yaml
	sudo MYIP=$(MYIP) docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/acord/ceilometer.yaml

containers:
	cd ../../../containers/xos; make devel
	cd ../../../containers/synchronizer; make

common_cloudlab:
	make -C ../common -f Makefile.cloudlab

common_devstack:
	make -C ../common -f Makefile.devstack

ceilometer_dashboard:
	#NOTE: The below dashboard install scripts assume
	#clouldlab openstack environment created using "OpenStack" profile
	#bash install_xos_ceilometer_dashboard.sh
	#bash install_ceilometer_patch.sh

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
