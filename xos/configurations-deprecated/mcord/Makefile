.PHONY: xos
xos: nodes.yaml images.yaml
	sudo docker-compose up -d
	../common/wait_for_xos_port.sh 8000
	sudo docker-compose run xos python /opt/xos/tosca/run.py none /opt/xos/configurations/common/fixtures.yaml
	sudo docker-compose run xos python /opt/xos/tosca/run.py none /opt/xos/configurations/common/mydeployment.yaml
	sudo docker-compose run xos python /opt/xos/tosca/run.py none /root/setup/setup.yaml
	sudo docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /root/setup/nodes.yaml
	sudo docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /root/setup/images.yaml
	sudo docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /root/setup/mgmt-net.yaml
	sudo docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /root/setup/mcord.yaml
	sudo docker exec mcord_xos_1 cp /opt/xos/configurations/mcord/xos_mcord_config /opt/xos/xos_configuration/
	sudo docker exec mcord_xos_1 touch /opt/xos/xos/settings.py

nodes.yaml:
	export SETUPDIR=.; bash ../common/make-nodes-yaml.sh

images.yaml:
	export SETUPDIR=.; bash ../common/make-images-yaml.sh

.PHONY: local_containers
local_containers:
	cd ../../../containers/xos; make devel
	cd ../../../containers/synchronizer; make
enter-xos:
	sudo docker exec -it mcord_xos_1 bash

enter-os:
	sudo docker exec -it mcord_xos_synchronizer_openstack_1 bash

enter-vbbu:
	sudo docker exec -it mcord_xos_synchronizer_vbbu_1 bash

enter-vpgwc:
	sudo docker exec -it mcord_xos_synchronizer_vpgwc_1 bash

upgrade_pkgs:
	sudo pip install httpie --upgrade

rebuild_xos:
	make -C ../../../containers/xos devel

rebuild_synchronizer:
	make -C ../../../containers/synchronizer

stop:
	docker-compose stop

rm:
	docker-compose stop; docker-compose rm

