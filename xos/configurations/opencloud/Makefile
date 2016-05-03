xos:
	sudo docker-compose up -d
	bash ./wait_for_xos.sh
	sudo docker-compose run xos python /opt/xos/tosca/run.py none /opt/xos/configurations/common/fixtures.yaml
	sudo docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/opencloud/opencloud.yaml

containers:
	cd ../../../containers/xos; make devel
	cd ../../../containers/synchronizer; make

stop:
	sudo docker-compose stop

showlogs:
	sudo docker-compose logs

rm: stop
	sudo docker-compose rm

ps:
	sudo docker-compose ps

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
