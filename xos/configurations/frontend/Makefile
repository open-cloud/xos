MYIP:=$(shell hostname -i)
CONFIG_DIR:=$(shell pwd)
DOCKER_COMPOSE_YML=./onboarding_docker_compose/docker-compose.yml
BOOTSTRAP_YML=./docker-compose-bootstrap.yml
DOCKER_PROJECT=frontend

frontend: prereqs bootstrap
#	bash ../common/wait_for_xos_file.sh onboarding-docker-compose/docker-compose.yml
#	cp onboarding-docker-compose/docker-compose.yml .
#	sudo docker-compose up -d
	bash ../common/wait_for_xos_port.sh 9999
	sudo docker-compose run xos_ui python /opt/xos/tosca/run.py none /opt/xos/configurations/common/fixtures.yaml
	sudo docker-compose run xos_ui python /opt/xos/tosca/run.py none /opt/xos/configurations/common/mydeployment.yaml
	sudo docker-compose run xos_ui python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/frontend/sample.yaml

prereqs:
	sudo make -f ../common/Makefile.prereqs

bootstrap:
	sudo rm -f onboarding-docker-compose/docker-compose.yml
	sudo rm -f docker-compose.yml
	sudo docker-compose -p $(DOCKER_PROJECT) -f docker-compose-bootstrap.yml up -d
	bash ../common/wait_for_xos_port.sh 9998
	sudo docker-compose -p $(DOCKER_PROJECT) -f $(BOOTSTRAP_YML) run -e CONFIG_DIR=$(CONFIG_DIR) xos_bootstrap_ui python /opt/xos/tosca/run.py none /opt/xos/configurations/frontend/xos.yaml

containers:
	cd ../../../containers/xos; make devel
	cd ../../../containers/synchronizer; make
	cd ../../../containers/onboarding_synchronizer; make
	#cd ../../../containers/xos; make devel

stop:
	sudo docker-compose -f $(BOOTSTRAP_YML) stop

showlogs:
	sudo docker-compose logs

rm: stop
	sudo docker-compose -f $(BOOTSTRAP_YML) rm

ps:
	sudo docker-compose ps

enter-xos:
	sudo docker exec -ti frontend_xos_1 bash

django-restart:
	sudo docker exec frontend_xos_1 touch /opt/xos/xos/settings.py

mock-cord-pod:
	echo "make sure to add '../vtn/files/xos_vtn_config:/opt/xos/xos_configuration/xos_vtn_config:ro' to volumes section of docker-compose.yml"
	sudo docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/common/fixtures.yaml
	sudo docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/frontend/mocks/mcord.yaml
	sudo docker exec frontend_xos_1 cp /opt/xos/configurations/mcord/xos_mcord_config /opt/xos/xos_configuration/
	sudo docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/cord-pod/mgmt-net.yaml
	sudo docker-compose run xos bash -c "echo somekey > /opt/xos/synchronizers/vcpe/vcpe_public_key; python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/cord-pod/cord-vtn-vsg.yaml"
	sudo docker exec frontend_xos_1 cp /opt/xos/configurations/cord-pod/xos_cord_config /opt/xos/xos_configuration/
	sudo docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/cord-pod/mgmt-net.yaml
	sudo docker-compose run xos bash -c "echo somekey > /opt/xos/synchronizers/vcpe/vcpe_public_key; python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/cord-pod/cord-vtn-vsg.yaml"
	sudo docker exec frontend_xos_1 cp /opt/xos/configurations/cord-pod/xos_cord_config /opt/xos/xos_configuration/
	sudo docker exec frontend_xos_1 touch /opt/xos/xos/settings.py

mock-mcord:
	# check this
	echo "make sure to add '../vtn/files/xos_vtn_config:/opt/xos/xos_configuration/xos_vtn_config:ro' to volumes section of docker-compose.yml"
	sudo docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/common/fixtures.yaml
	sudo docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/cord-pod/mgmt-net.yaml
	sudo docker-compose run xos bash -c "echo somekey > /opt/xos/synchronizers/vcpe/vcpe_public_key; python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/cord-pod/cord-vtn-vsg.yaml"
	sudo docker exec frontend_xos_1 cp /opt/xos/configurations/mcord/xos_mcord_config /opt/xos/xos_configuration/
	sudo docker exec frontend_xos_1 touch /opt/xos/xos/settings.py

exampleservice:
	mkdir -p key_import
	# fake keys are fine
	echo somekey > key_import/exampleservice_rsa
	echo somekey > key_import/exampleservice_rsa.pub
	sudo docker-compose run xos_ui python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/onboard/exampleservice/exampleservice-onboard.yaml
