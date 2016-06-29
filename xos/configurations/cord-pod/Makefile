CONFIG_DIR:=$(shell pwd)
DOCKER_COMPOSE_YML=./onboarding-docker-compose/docker-compose.yml
BOOTSTRAP_YML=./docker-compose-bootstrap.yml
DOCKER_PROJECT=cordpod
BOOTSTRAP_PROJECT=cordpodbs
XOS_BOOTSTRAP_PORT=81
XOS_UI_PORT=80
ADMIN_USERNAME=padmin@vicci.org
ADMIN_PASSWORD=letmein
RUN_TOSCA_BOOTSTRAP=python ../common/run_tosca.py $(XOS_BOOTSTRAP_PORT) $(ADMIN_USERNAME) $(ADMIN_PASSWORD)
RUN_TOSCA=python ../common/run_tosca.py $(XOS_UI_PORT) $(ADMIN_USERNAME) $(ADMIN_PASSWORD)
SERVICE_DIR=../../../../xos_services

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
	sudo CONFIG_DIR=$(CONFIG_DIR) docker-compose -p $(BOOTSTRAP_PROJECT) -f $(BOOTSTRAP_YML) up -d
	bash ../common/wait_for_xos_port.sh 81
	sudo docker-compose -p $(BOOTSTRAP_PROJECT) -f $(BOOTSTRAP_YML) run xos_bootstrap_ui python /opt/xos/tosca/run.py none /opt/xos/configurations/common/fixtures.yaml
	sudo docker-compose -p $(BOOTSTRAP_PROJECT) -f $(BOOTSTRAP_YML) run xos_bootstrap_ui python /opt/xos/tosca/run.py none /opt/xos/configurations/common/mydeployment.yaml
	$(RUN_TOSCA_BOOTSTRAP) xos.yaml

download_services:
	make -f ../common/Makefile.services

update_services:
	make -f ../common/Makefile.services update

onboarding:
	echo "[ONBOARDING]"
	# on-board any services here
	bash ../common/wait_for_onboarding_ready.sh 81 xos
	$(RUN_TOSCA_BOOTSTRAP) ../common/disable-onboarding.yaml
	sudo cp id_rsa key_import/vsg_rsa
	sudo cp id_rsa.pub key_import/vsg_rsa.pub
	sudo cp id_rsa key_import/volt_rsa
	sudo cp id_rsa.pub key_import/volt_rsa.pub
	sudo cp id_rsa key_import/onos_rsa
	sudo cp id_rsa key_import/onos_rsa.pub
	$(RUN_TOSCA_BOOTSTRAP) $(SERVICE_DIR)/vrouter/xos/vrouter-onboard.yaml
	$(RUN_TOSCA_BOOTSTRAP) $(SERVICE_DIR)/olt/xos/volt-onboard.yaml
	$(RUN_TOSCA_BOOTSTRAP) $(SERVICE_DIR)/vsg/xos/vsg-onboard.yaml
	$(RUN_TOSCA_BOOTSTRAP) $(SERVICE_DIR)/vtn/xos/vtn-onboard.yaml
	$(RUN_TOSCA_BOOTSTRAP) $(SERVICE_DIR)/onos-service/xos/onos-onboard.yaml
	$(RUN_TOSCA_BOOTSTRAP) $(SERVICE_DIR)/fabric/xos/\fabric-onboard.yaml
	$(RUN_TOSCA_BOOTSTRAP) $(SERVICE_DIR)/vtr/xos/vtr-onboard.yaml
	$(RUN_TOSCA_BOOTSTRAP) synchronizers.yaml
	$(RUN_TOSCA_BOOTSTRAP) ../common/enable-onboarding.yaml
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
	$(RUN_TOSCA) setup.yaml
	$(RUN_TOSCA) nodes.yaml
	$(RUN_TOSCA) images.yaml

vtn: vtn-external.yaml
	$(RUN_TOSCA) vtn-external.yaml

fabric: fabric.yaml
	$(RUN_TOSCA) fabric.yaml

cord: vsg_custom_images
	$(RUN_TOSCA) mgmt-net.yaml
	$(RUN_TOSCA) cord-vtn-vsg.yaml
	$(RUN_TOSCA) cord-volt-devices.yaml

clean-nodes:
	rm -f nodes.yaml

update-nodes: nodes.yaml
	$(RUN_TOSCA) nodes.yaml

new-nodes: clean-nodes update-nodes vtn

exampleservice: onboard-exampleservice
	$(RUN_TOSCA) pod-exampleservice.yaml

onboard-exampleservice:
	sudo cp id_rsa key_import/exampleservice_rsa
	sudo cp id_rsa.pub key_import/exampleservice_rsa.pub
	$(RUN_TOSCA_BOOSTRAP) $(SERVICE_DIR)/exampleservice/exampleservice-onboard.yaml
	bash ../common/wait_for_onboarding_ready.sh 81 services/exampleservice
	bash ../common/wait_for_onboarding_ready.sh 81 xos
	bash ../common/wait_for_xos_port.sh 80

cord-monitoringservice: ceilometer_custom_images cord onboard-monitoringservice
	$(RUN_TOSCA) monitoringservice.yaml

onboard-monitoringservice: download-monitoringservice
	sudo cp id_rsa key_import/monitoringservice_rsa
	sudo cp id_rsa.pub key_import/monitoringservice_rsa.pub
	$(RUN_TOSCA_BOOTSTRAP) $(SERVICE_DIR)/monitoring/xos/monitoring-onboard.yaml
	bash ../common/wait_for_onboarding_ready.sh 81 services/monitoring
	bash ../common/wait_for_onboarding_ready.sh 81 xos
	bash ../common/wait_for_xos_port.sh 80

download-monitoringservice:
	make -f ../common/Makefile.services monitoring_services

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
