MYIP:=$(shell hostname -i)

cloudlab: common_cloudlab xos

devstack: upgrade_pkgs common_devstack xos

xos:
	sudo MYIP=$(MYIP) docker-compose up -d
	bash ../common/wait_for_xos.sh
	sudo MYIP=$(MYIP) docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/common/base.yaml
	sudo MYIP=$(MYIP) docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /root/setup/nodes.yaml

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

enter-xos:
	sudo docker exec -it devel_xos_1 bash

enter-synchronizer:
	sudo docker exec -it devel_xos_synchronizer_openstack_1 bash

upgrade_pkgs:
	sudo pip install httpie --upgrade

rebuild_xos:
	make -C ../../../containers/xos devel

rebuild_synchronizer:
	make -C ../../../containers/synchronizer

cleanup_docker: rm
	sudo docker rm -v $(docker ps -a -q -f status=exited) || true
	docker rm -v $(docker ps -a -q -f status=exited) || true
	sudo docker rmi $(docker images -qf "dangling=true") || true
	docker rmi $(docker images -qf "dangling=true") || true
	sudo docker run -v /var/run/docker.sock:/var/run/docker.sock -v /var/lib/docker:/var/lib/docker --rm martin/docker-cleanup-volumes || true
