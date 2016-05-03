MYIP:=$(shell hostname -i)

cloudlab: common_cloudlab xos

xos:
	sudo MYIP=$(MYIP) docker-compose up -d
	bash ../common/wait_for_xos.sh
	sudo docker-compose run xos python /opt/xos/tosca/run.py none /opt/xos/configurations/common/fixtures.yaml
	sudo docker-compose run xos python /opt/xos/tosca/run.py none /opt/xos/configurations/common/mydeployment.yaml
	sudo MYIP=$(MYIP) docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/common/cloudlab-openstack.yaml
	sudo MYIP=$(MYIP) docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /root/setup/nodes.yaml

frontend:
	sudo make -f ../common/Makefile.prereqs
	sudo docker-compose up -d
	bash ../common/wait_for_xos.sh
	sudo docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/frontend/sample.yaml

containers:
	cd ../../../containers/xos; make devel
	cd ../../../containers/synchronizer; make
	cd ../../../containers/openvpn; make

common_cloudlab:
	make -C ../common -f Makefile.cloudlab

stop:
	sudo MYIP=$(MYIP) docker-compose stop

showlogs:
	sudo MYIP=$(MYIP) docker-compose logs

rm: stop
	sudo MYIP=$(MYIP) docker-compose rm

ps:
	sudo MYIP=$(MYIP) docker-compose ps

enter-xos:
	sudo docker exec -it openvpn_xos_1 bash

enter-synchronizer:
	sudo docker exec -it openvpn_xos_synchronizer_openvpn_1 bash

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
	socker rmi $(docker images -qf "dangling=true") || true
	sudo docker run -v /var/run/docker.sock:/var/run/docker.sock -v /var/lib/docker:/var/lib/docker --rm martin/docker-cleanup-volumes || true
