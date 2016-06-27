MYIP:=$(shell hostname -i)
CONFIG_DIR:=$(shell pwd)
DOCKER_COMPOSE_YML=./onboarding-docker-compose/docker-compose.yml
BOOTSTRAP_YML=./docker-compose-bootstrap.yml
DOCKER_PROJECT=frontend
BOOTSTRAP_PROJECT=frontendbs
XOS_BOOTSTRAP_PORT=9998
XOS_UI_PORT=9999
ADMIN_USERNAME=padmin@vicci.org
ADMIN_PASSWORD=letmein
RUN_TOSCA_BOOTSTRAP=python ../common/run_tosca.py $(XOS_BOOTSTRAP_PORT) $(ADMIN_USERNAME) $(ADMIN_PASSWORD)
RUN_TOSCA=python ../common/run_tosca.py $(XOS_UI_PORT) $(ADMIN_USERNAME) $(ADMIN_PASSWORD)
SERVICE_DIR=../../../../xos_services

frontend: prereqs dirs download_services bootstrap onboarding frontendconfig

prereqs:
	sudo make -f ../common/Makefile.prereqs

dirs:
	# if this directory doesn't exist, then docker-compose will create it with root permission
	mkdir -p key_import
	mkdir -p onboarding-docker-compose

download_services:
	make -f ../common/Makefile.services

update_services:
	make -f ../common/Makefile.services update

bootstrap:
	echo "[BOOTSTRAP]"
	sudo rm -f onboarding-docker-compose/docker-compose.yml
	sudo CONFIG_DIR=$(CONFIG_DIR) docker-compose -p $(BOOTSTRAP_PROJECT) -f $(BOOTSTRAP_YML) up -d
	bash ../common/wait_for_xos_port.sh $(XOS_BOOTSTRAP_PORT)
	sudo docker-compose -p $(BOOTSTRAP_PROJECT) -f $(BOOTSTRAP_YML) run xos_bootstrap_ui python /opt/xos/tosca/run.py none /opt/xos/configurations/common/fixtures.yaml
	sudo docker-compose -p $(BOOTSTRAP_PROJECT) -f $(BOOTSTRAP_YML) run xos_bootstrap_ui python /opt/xos/tosca/run.py none /opt/xos/configurations/common/mydeployment.yaml
	$(RUN_TOSCA_BOOTSTRAP) xos.yaml

onboarding:
	echo "[ONBOARDING]"
	# on-board any services here
	bash ../common/wait_for_onboarding_ready.sh $(XOS_BOOTSTRAP_PORT) xos
	bash ../common/wait_for_xos_port.sh $(XOS_UI_PORT)

frontendconfig:
	echo "[FRONTENDCONFIG]"
	$(RUN_TOSCA) sample.yaml

containers:
	cd ../../../containers/xos; make devel
	cd ../../../containers/synchronizer; make
	cd ../../../containers/onboarding_synchronizer; make
	#cd ../../../containers/xos; make devel

stop:
	test ! -s $(DOCKER_COMPOSE_YML) || sudo docker-compose -p $(DOCKER_PROJECT) -f $(DOCKER_COMPOSE_YML) stop
	sudo docker-compose -p $(BOOTSTRAP_PROJECT) -f $(BOOTSTRAP_YML) stop

showlogs:
	sudo docker-compose -p $(BOOTSTRAP_PROJECT) -f $(BOOTSTRAP_YML) logs

rm: stop
	test ! -s $(DOCKER_COMPOSE_YML) || sudo docker-compose -p $(DOCKER_PROJECT) -f $(DOCKER_COMPOSE_YML) rm
	sudo docker-compose -p $(BOOTSTRAP_PROJECT) -f $(BOOTSTRAP_YML) rm

ps:
	sudo docker-compose ps

enter-xos:
	sudo docker exec -ti frontend_xos_ui_1 bash

django-restart:
	sudo docker exec frontend_xos_ui_1 touch /opt/xos/xos/settings.py

clean-config-folder:
	sudo docker exec frontend_xos_ui_1 rm -f /opt/xos/xos_configuration/xos_mcord_config
	sudo docker exec frontend_xos_ui_1 rm -f /opt/xos/xos_configuration/xos_cord_config

mock-cord-pod: onboard-cord-pod
	$(RUN_TOSCA) ../cord-pod/mgmt-net.yaml
	$(RUN_TOSCA) ../cord-pod/cord-vtn-vsg.yaml
	$(RUN_TOSCA) ../cord-pod/cord-volt-devices.yaml
	sudo docker exec frontend_xos_ui_1 cp /opt/xos/configurations/cord-pod/xos_cord_config /opt/xos/xos_configuration/
	sudo docker exec frontend_xos_ui_1 touch /opt/xos/xos/settings.py

onboard-cord-pod:
	sudo bash -c "echo somekey > key_import/vsg_rsa"
	sudo bash -c "echo somekey > key_import/vsg_rsa.pub"
	sudo bash -c "echo somekey > key_import/volt_rsa"
	sudo bash -c "echo somekey > key_import/volt_rsa.pub"
	$(RUN_TOSCA_BOOTSTRAP) $(SERVICE_DIR)/vrouter/xos/vrouter-onboard.yaml
	$(RUN_TOSCA_BOOTSTRAP) $(SERVICE_DIR)/olt/xos/volt-onboard.yaml
	$(RUN_TOSCA_BOOTSTRAP) $(SERVICE_DIR)/vsg/xos/vsg-onboard.yaml
	bash ../common/wait_for_onboarding_ready.sh 9998 services/vrouter
	bash ../common/wait_for_onboarding_ready.sh 9998 services/volt
	bash ../common/wait_for_onboarding_ready.sh 9998 services/vsg
	bash ../common/wait_for_onboarding_ready.sh $(XOS_BOOTSTRAP_PORT) xos
	bash ../common/wait_for_xos_port.sh $(XOS_UI_PORT)

mock-mcord:
	# check this
	$(RUN_TOSCA) ../cord-pod/mgmt-net.yaml
	$(RUN_TOSCA) mocks/mcord.yaml
	sudo docker exec frontend_xos_ui_1 cp /opt/xos/configurations/mcord/xos_mcord_config /opt/xos/xos_configuration/
	sudo docker exec frontend_xos_ui_1 touch /opt/xos/xos/settings.py

exampleservice:
	mkdir -p key_import
	# fake keys are fine
	sudo bash -c "echo somekey > key_import/exampleservice_rsa"
	sudo bash -c "echo somekey > key_import/exampleservice_rsa.pub"
	$(RUN_TOSCA_BOOTSTRAP) $(SERVICE_DIR)/exampleservice/xos/exampleservice-onboard.yaml
	bash ../common/wait_for_onboarding_ready.sh 9998 services/exampleservice
	bash ../common/wait_for_onboarding_ready.sh 9998 xos
