MYIP:=$(shell hostname -i)

cloudlab: common_cloudlab xos

devstack: upgrade_pkgs common_devstack devstack_net_fix xos

xos:
	sudo MYIP=$(MYIP) docker-compose up -d
	bash ../common/wait_for_xos.sh
	sudo docker-compose run xos python /opt/xos/tosca/run.py none /opt/xos/configurations/common/fixtures.yaml
	sudo docker-compose run xos python /opt/xos/tosca/run.py none /opt/xos/configurations/common/mydeployment.yaml
	sudo MYIP=$(MYIP) docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/common/cloudlab-openstack.yaml
	sudo MYIP=$(MYIP) docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /root/setup/nodes.yaml
	sudo MYIP=$(MYIP) docker-compose run xos bash -c "cd /opt/xos/tosca/tests; python ./alltests.py"
	sudo MYIP=$(MYIP) docker-compose run xos bash -c "cd /opt/xos/tosca/tests; python ./allObserverTests.py"

containers:
	cd ../../../containers/xos; make devel
	cd ../../../containers/synchronizer; make

common_cloudlab:
	make -C ../common -f Makefile.cloudlab

common_devstack:
	make -C ../common -f Makefile.devstack

stop:
	sudo MYIP=$(MYIP) docker-compose stop

showlogs:
	sudo MYIP=$(MYIP) docker-compose logs

rm: stop
	sudo MYIP=$(MYIP) docker-compose rm

ps:
	sudo MYIP=$(MYIP) docker-compose ps

devstack_net_fix:
	sudo ../common/devstack/net-fix.sh
	sudo bash -c "source ../setup/admin-openrc.sh; neutron subnet-update private-subnet --dns-nameservers list=true 8.8.8.8 8.8.4.4"

upgrade_pkgs:
	sudo pip install httpie --upgrade
