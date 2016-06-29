SETUPDIR:=../setup
MYIP:=$(shell hostname -i)

cloudlab: common_cloudlab ansible_hosts xos

devstack: upgrade_pkgs common_devstack ansible_hosts xos

xos: vtn_network_cfg_json
	sudo MYIP=$(MYIP) docker-compose up -d
	bash ../common/wait_for_xos.sh
	sudo MYIP=$(MYIP) docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/common/fixtures.yaml
	sudo MYIP=$(MYIP) docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/common/base.yaml
	sudo MYIP=$(MYIP) docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /root/setup/nodes.yaml
	sudo MYIP=$(MYIP) docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/vtn/vtn.yaml

containers:
	cd ../../../containers/xos; make devel
	cd ../../../containers/synchronizer; make

common_cloudlab:
	make -C ../common -f Makefile.cloudlab

common_devstack:
	make -C ../common -f Makefile.devstack

vtn_network_cfg_json:
	export SETUPDIR=$(SETUPDIR); bash ../cord/make-vtn-networkconfig-json.sh

ansible_hosts:
	sudo bash -c "export SETUPDIR=$(SETUPDIR); scripts/gen-inventory.sh"

stop:
	sudo MYIP=$(MYIP) docker-compose stop

showlogs:
	sudo MYIP=$(MYIP) docker-compose logs

rm: stop
	sudo MYIP=$(MYIP) docker-compose rm

ps:
	sudo MYIP=$(MYIP) docker-compose ps

enter-xos:
	sudo docker exec -it vtn_xos_1 bash

enter-synchronizer:
	sudo docker exec -it vtn_xos_synchronizer_openstack_1 bash

upgrade_pkgs:
	sudo pip install httpie --upgrade

destroy-networks:
	sudo ../../tools/destroy-all-networks.sh
