MYIP:=$(shell hostname -i)

cloudlab: common_cloudlab local_containers xos

devstack: upgrade_pkgs common_devstack local_containers xos

xos:
	sudo MYIP=$(MYIP) docker-compose up -d
	bash ../common/wait_for_xos.sh
	sudo docker-compose run xos python /opt/xos/tosca/run.py none /opt/xos/configurations/common/fixtures.yaml
	sudo docker-compose run xos python /opt/xos/tosca/run.py none /opt/xos/configurations/common/mydeployment.yaml
	sudo MYIP=$(MYIP) docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/common/cloudlab-openstack.yaml
	sudo MYIP=$(MYIP) docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /root/setup/nodes.yaml

common_cloudlab:
	make -C ../common -f Makefile.cloudlab

common_devstack:
	make -C ../common -f Makefile.devstack

base:
	make -C ../../../containers/xos base

local_containers:
	echo "" > ../../../containers/xos/local_certs.crt
	for CRT in $$(ls /usr/local/share/ca-certificates/*) ; do \
		echo Adding Certificate: $$CRT ;\
		cat $$CRT >> ../../../containers/xos/local_certs.crt ;\
		echo "" >> ../../../containers/xos/local_certs.crt ;\
	done
	make -C ../../../containers/xos devel
	make -C ../../../containers/synchronizer

stop:
	sudo MYIP=$(MYIP) docker-compose stop

showlogs:
	sudo MYIP=$(MYIP) docker-compose logs

rm: stop
	sudo MYIP=$(MYIP) docker-compose rm

ps:
	sudo MYIP=$(MYIP) docker-compose ps

enter-xos:
	sudo docker exec -it devel_xos_1 bash

enter-synchronizer:
	sudo docker exec -it devel_xos_synchronizer_openstack_1 bash

upgrade_pkgs:
	sudo pip install httpie --upgrade

