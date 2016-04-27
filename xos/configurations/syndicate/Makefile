MYIP:=$(shell hostname -i)

cloudlab: common_cloudlab xos

devstack: upgrade_pkgs common_devstack xos

xos: syndicate_config
	sudo MYIP=$(MYIP) docker-compose up -d
	bash ../common/wait_for_xos.sh
	sudo docker-compose run xos python /opt/xos/tosca/run.py none /opt/xos/configurations/common/fixtures.yaml
	sudo docker-compose run xos python /opt/xos/tosca/run.py none /opt/xos/configurations/common/mydeployment.yaml
	sudo MYIP=$(MYIP) docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/common/cloudlab-openstack.yaml
	sudo MYIP=$(MYIP) docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /root/setup/nodes.yaml

containers:
	cd ../../../containers/xos; make devel
	cd ../../../containers/synchronizer; make
	cd ../../../containers/syndicate-ms; make

# see Makefiles on this project: https://github.com/syndicate-storage/syndicate-core
include MS.mk
syndicate_config: ms/admin_info.py ms/app.yaml

common_cloudlab:
	make -C ../common -f Makefile.cloudlab

common_devstack:
	make -C ../common -f Makefile.devstack

stop:
	sudo MYIP=$(MYIP) docker-compose stop

showlogs:
	sudo MYIP=$(MYIP) docker-compose logs

rm: stop
	sudo MYIP=$(MYIP) docker-compose rm --force

ps:
	sudo MYIP=$(MYIP) docker-compose ps

enter-xos:
	sudo docker exec -it syndicate_xos_1 bash

enter-synchronizer:
	sudo docker exec -it syndicate_xos_synchronizer_openstack_1 bash

enter-ms:
	sudo docker exec -it syndicate_xos_syndicate_ms_1 bash

upgrade_pkgs:
	sudo pip install httpie --upgrade

rebuild_xos:
	make -C ../../../containers/xos devel

rebuild_synchronizer:
	make -C ../../../containers/synchronizer

rebuild_syndicate_ms:
	make -C ../../../containers/syndicate-ms

