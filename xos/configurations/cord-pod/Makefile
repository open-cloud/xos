CONFIG_DIR:=$(shell pwd)
DOCKER_COMPOSE_YML=./onboarding-docker-compose/docker-compose.yml
BOOTSTRAP_YML=./docker-compose-bootstrap.yml
DOCKER_PROJECT=cordpod
BOOTSTRAP_PROJECT=cordpodbs

.PHONY: xos
xos: prereqs dirs download_services bootstrap onboarding podconfig

prereqs:
	sudo make -f ../common/Makefile.prereqs

dirs:
	# if this directory doesn't exist, then docker-compose will create it with root permission
	mkdir -p key_import
	mkdir -p onboarding-docker-compose

bootstrap:
	echo "[BOOTSTRAP]"
	sudo rm -f onboarding-docker-compose/docker-compose.yml
	sudo docker-compose -p $(BOOTSTRAP_PROJECT) -f $(BOOTSTRAP_YML) up -d
	bash ../common/wait_for_xos_port.sh 81
	sudo docker-compose -p $(BOOTSTRAP_PROJECT) -f $(BOOTSTRAP_YML) run -e CONFIG_DIR=$(CONFIG_DIR) xos_bootstrap_ui python /opt/xos/tosca/run.py none /opt/xos/configurations/cord-pod/xos.yaml

download_services:
	make -f ../common/Makefile.services

update_services:
	make -f ../common/Makefile.services update

onboarding:
	echo "[ONBOARDING]"
	# on-board any services here
	bash ../common/wait_for_onboarding_ready.sh 81 xos
	sudo docker-compose -p $(BOOTSTRAP_PROJECT) -f $(BOOTSTRAP_YML) run xos_bootstrap_ui python /opt/xos/tosca/run.py None /opt/xos/configurations/common/disable-onboarding.yaml
	sudo cp id_rsa key_import/vsg_rsa
	sudo cp id_rsa.pub key_import/vsg_rsa.pub
	sudo cp id_rsa key_import/volt_rsa
	sudo cp id_rsa.pub key_import/volt_rsa.pub
	sudo cp id_rsa key_import/onos_rsa
	sudo cp id_rsa key_import/onos_rsa.pub
	sudo docker-compose -p $(BOOTSTRAP_PROJECT) -f $(BOOTSTRAP_YML) run xos_bootstrap_ui python /opt/xos/tosca/run.py None /opt/xos_services/vrouter/xos/vrouter-onboard.yaml
	sudo docker-compose -p $(BOOTSTRAP_PROJECT) -f $(BOOTSTRAP_YML) run xos_bootstrap_ui python /opt/xos/tosca/run.py None /opt/xos_services/olt/xos/volt-onboard.yaml
	sudo docker-compose -p $(BOOTSTRAP_PROJECT) -f $(BOOTSTRAP_YML) run xos_bootstrap_ui python /opt/xos/tosca/run.py None /opt/xos_services/vsg/xos/vsg-onboard.yaml
	sudo docker-compose -p $(BOOTSTRAP_PROJECT) -f $(BOOTSTRAP_YML) run xos_bootstrap_ui python /opt/xos/tosca/run.py None /opt/xos_services/vtn/xos/vtn-onboard.yaml
	sudo docker-compose -p $(BOOTSTRAP_PROJECT) -f $(BOOTSTRAP_YML) run xos_bootstrap_ui python /opt/xos/tosca/run.py None /opt/xos_services/onos-service/xos/onos-onboard.yaml
	sudo docker-compose -p $(BOOTSTRAP_PROJECT) -f $(BOOTSTRAP_YML) run xos_bootstrap_ui python /opt/xos/tosca/run.py None /opt/xos_services/fabric/xos/\fabric-onboard.yaml
	sudo docker-compose -p $(BOOTSTRAP_PROJECT) -f $(BOOTSTRAP_YML) run xos_bootstrap_ui python /opt/xos/tosca/run.py None /opt/xos_services/vtr/xos/vtr-onboard.yaml
	sudo docker-compose -p $(BOOTSTRAP_PROJECT) -f $(BOOTSTRAP_YML) run xos_bootstrap_ui python /opt/xos/tosca/run.py None /opt/xos/configurations/cord-pod/synchronizers.yaml
	sudo docker-compose -p $(BOOTSTRAP_PROJECT) -f $(BOOTSTRAP_YML) run xos_bootstrap_ui python /opt/xos/tosca/run.py None /opt/xos/configurations/common/enable-onboarding.yaml
	bash ../common/wait_for_onboarding_ready.sh 81 services/vrouter
	bash ../common/wait_for_onboarding_ready.sh 81 services/volt
	bash ../common/wait_for_onboarding_ready.sh 81 services/vsg
	bash ../common/wait_for_onboarding_ready.sh 81 services/vtn
	bash ../common/wait_for_onboarding_ready.sh 81 services/onos
	bash ../common/wait_for_onboarding_ready.sh 81 services/fabric
	bash ../common/wait_for_onboarding_ready.sh 81 services/vtr
	bash ../common/wait_for_onboarding_ready.sh 81 xos
	bash ../common/wait_for_xos_port.sh 80

podconfig: nodes.yaml images.yaml
	echo "[PODCONFIG]"
	sudo docker-compose -p $(DOCKER_PROJECT) -f $(DOCKER_COMPOSE_YML) run xos_ui python /opt/xos/tosca/run.py none /opt/xos/configurations/common/fixtures.yaml
	sudo docker-compose -p $(DOCKER_PROJECT) -f $(DOCKER_COMPOSE_YML) run xos_ui python /opt/xos/tosca/run.py none /opt/xos/configurations/common/mydeployment.yaml
	sudo docker-compose -p $(DOCKER_PROJECT) -f $(DOCKER_COMPOSE_YML) run xos_ui python /opt/xos/tosca/run.py padmin@vicci.org /root/setup/setup.yaml
	sudo docker-compose -p $(DOCKER_PROJECT) -f $(DOCKER_COMPOSE_YML) run xos_ui python /opt/xos/tosca/run.py padmin@vicci.org /root/setup/nodes.yaml
	sudo docker-compose -p $(DOCKER_PROJECT) -f $(DOCKER_COMPOSE_YML) run xos_ui python /opt/xos/tosca/run.py padmin@vicci.org /root/setup/images.yaml

vtn: vtn-external.yaml
	sudo docker-compose -p $(DOCKER_PROJECT) -f $(DOCKER_COMPOSE_YML) run xos_ui python /opt/xos/tosca/run.py padmin@vicci.org /root/setup/vtn-external.yaml

fabric: fabric.yaml
	sudo docker-compose -p $(DOCKER_PROJECT) -f $(DOCKER_COMPOSE_YML) run xos_ui python /opt/xos/tosca/run.py padmin@vicci.org /root/setup/fabric.yaml

cord: vsg_custom_images
	sudo docker-compose -p $(DOCKER_PROJECT) -f $(DOCKER_COMPOSE_YML) run xos_ui python /opt/xos/tosca/run.py padmin@vicci.org /root/setup/mgmt-net.yaml
	sudo docker-compose -p $(DOCKER_PROJECT) -f $(DOCKER_COMPOSE_YML) run xos_ui python /opt/xos/tosca/run.py padmin@vicci.org /root/setup/cord-vtn-vsg.yaml
	sudo docker-compose -p $(DOCKER_PROJECT) -f $(DOCKER_COMPOSE_YML) run xos_ui python /opt/xos/tosca/run.py padmin@vicci.org /root/setup/cord-volt-devices.yaml

clean-nodes:
	rm -f nodes.yaml

update-nodes: nodes.yaml
	sudo docker-compose -p $(DOCKER_PROJECT) -f $(DOCKER_COMPOSE_YML) run xos_ui python /opt/xos/tosca/run.py padmin@vicci.org /root/setup/nodes.yaml

new-nodes: clean-nodes update-nodes vtn

exampleservice: onboard-exampleservice
	sudo docker-compose -p $(DOCKER_PROJECT) -f $(DOCKER_COMPOSE_YML) run xos_ui python /opt/xos/tosca/run.py padmin@vicci.org /root/setup/pod-exampleservice.yaml

onboard-exampleservice:
	sudo cp id_rsa key_import/exampleservice_rsa
	sudo cp id_rsa.pub key_import/exampleservice_rsa.pub
	sudo docker-compose -p $(BOOTSTRAP_PROJECT) -f $(BOOTSTRAP_YML) run xos_bootstrap_ui python /opt/xos/tosca/run.py None /opt/xos/onboard/exampleservice/exampleservice-onboard.yaml
	bash ../common/wait_for_onboarding_ready.sh 81 services/exampleservice
	bash ../common/wait_for_onboarding_ready.sh 81 xos
	bash ../common/wait_for_xos_port.sh 80

cord-ceilometer: ceilometer_custom_images cord onboard-ceilometer
	sudo docker-compose  -p $(DOCKER_PROJECT) -f $(DOCKER_COMPOSE_YML) run xos_ui python /opt/xos/tosca/run.py padmin@vicci.org /root/setup/ceilometer.yaml

onboard-ceilometer:
	sudo cp id_rsa key_import/monitoring_channel_rsa
	sudo cp id_rsa.pub key_import/monitoring_channel_rsa.pub
	sudo docker-compose -p $(BOOTSTRAP_PROJECT) -f $(BOOTSTRAP_YML) run xos_bootstrap_ui python /opt/xos/tosca/run.py None /opt/xos/onboard/ceilometer/ceilometer-onboard.yaml
	bash ../common/wait_for_onboarding_ready.sh 81 services/ceilometer
	bash ../common/wait_for_onboarding_ready.sh 81 xos
	bash ../common/wait_for_xos_port.sh 80

nodes.yaml:
	export SETUPDIR=.; bash ../common/make-nodes-yaml.sh

images.yaml:
	export SETUPDIR=.; bash ../common/make-images-yaml.sh

vtn-external.yaml:
	export SETUPDIR=.; bash ./make-vtn-external-yaml.sh

fabric.yaml:
	export SETUPDIR=.; bash ./make-fabric-yaml.sh

virtualbng_json:
	export SETUPDIR=.; bash ./make-virtualbng-json.sh

vtn_network_cfg_json:
	export SETUPDIR=.; bash ./make-vtn-networkconfig-json.sh

stop:
	test ! -s $(DOCKER_COMPOSE_YML) || sudo docker-compose -p $(DOCKER_PROJECT) -f $(DOCKER_COMPOSE_YML) stop
	sudo docker-compose -p $(BOOTSTRAP_PROJECT) -f $(BOOTSTRAP_YML) stop

rm:
	test ! -s $(DOCKER_COMPOSE_YML) || sudo docker-compose -p $(DOCKER_PROJECT) -f $(DOCKER_COMPOSE_YML) rm
	sudo docker-compose -p $(BOOTSTRAP_PROJECT) -f $(BOOTSTRAP_YML) rm

showlogs:
	sudo MYIP=$(MYIP) docker-compose logs

cleanup: stop rm
	./cleanup.sh
	bash -c "source ./admin-openrc.sh; nova list --all-tenants; neutron net-list"

ceilometer_custom_images: images/ceilometer-trusty-server-multi-nic.img
	bash -c "source ./admin-openrc.sh; glance image-show ceilometer-trusty-server-multi-nic || glance image-create --name ceilometer-trusty-server-multi-nic --disk-format qcow2 --file ./images/ceilometer-trusty-server-multi-nic.img --container-format bare"

vsg_custom_images: images/vsg-1.0.img
	bash -c "source ./admin-openrc.sh; glance image-show vsg-1.0 || glance image-create --name vsg-1.0 --disk-format qcow2 --file ./images/vsg-1.0.img --container-format bare"

images/ceilometer-trusty-server-multi-nic.img: images
	wget http://www.vicci.org/cord/ceilometer-trusty-server-multi-nic.compressed.qcow2 -P ./images
	mv ./images/ceilometer-trusty-server-multi-nic.compressed.qcow2 ./images/ceilometer-trusty-server-multi-nic.img

images/vsg-1.0.img: images
	wget http://www.vicci.org/cord/vsg-1.0.img -P ./images

images:
	mkdir -p ./images

.PHONY: local_containers
local_containers:
	echo "" > ../../../containers/xos/local_certs.crt
	for CRT in $$(ls /usr/local/share/ca-certificates/*) ; do \
		echo Adding Certificate: $$CRT ;\
		cat $$CRT >> ../../../containers/xos/local_certs.crt ;\
		echo "" >> ../../../containers/xos/local_certs.crt ;\
	done
	cd ../../../containers/xos; make devel
	cd ../../../containers/synchronizer; make
	cd ../../../containers/onboarding_synchronizer; make
