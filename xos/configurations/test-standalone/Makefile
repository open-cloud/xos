MYIP:=$(shell hostname -i)
CONFIG_DIR:=$(shell pwd)
DOCKER_COMPOSE_YML=./onboarding-docker-compose/docker-compose.yml
BOOTSTRAP_YML=./docker-compose-bootstrap.yml
DOCKER_PROJECT=teststandalone
XOS_BOOTSTRAP_PORT=9998
XOS_UI_PORT=9999

define TRUNCATE_FN
	CREATE OR REPLACE FUNCTION truncate_tables(username IN VARCHAR) RETURNS void AS $$$$
	DECLARE
			statements CURSOR FOR
					SELECT tablename FROM pg_tables
					WHERE tableowner = username AND schemaname = 'public';
	BEGIN
			FOR stmt IN statements LOOP
					EXECUTE 'TRUNCATE TABLE ' || quote_ident(stmt.tablename) || ' CASCADE;';
			END LOOP;
	END;
	$$$$ LANGUAGE plpgsql;
endef
export TRUNCATE_FN

prepare: xos
	sudo docker exec -i teststandalone_xos_1 bash -c "cd /opt/xos/tests/api; npm install --production"
	sudo docker exec teststandalone_xos_1 pip install dredd_hooks

xos: prereqs bootstrap onboarding

prereqs:
	sudo make -f ../common/Makefile.prereqs

bootstrap:
	echo "[BOOTSTRAP]"
	sudo rm -f onboarding-docker-compose/docker-compose.yml
	sudo docker-compose -p $(DOCKER_PROJECT) -f docker-compose-bootstrap.yml up -d
	bash ../common/wait_for_xos_port.sh 9998
	sudo docker-compose -p $(DOCKER_PROJECT) -f $(BOOTSTRAP_YML) run -e CONFIG_DIR=$(CONFIG_DIR) xos_bootstrap_ui python /opt/xos/tosca/run.py none /opt/xos/configurations/test-standalone/xos.yaml

onboarding:
	echo "[ONBOARDING]"
	bash ../common/wait_for_onboarding_ready.sh 9998 xos
	sudo docker-compose -p $(DOCKER_PROJECT) -f $(BOOTSTRAP_YML) run xos_bootstrap_ui python /opt/xos/tosca/run.py None /opt/xos/configurations/common/enable-onboarding.yaml
	sudo docker-compose -p $(DOCKER_PROJECT) -f $(BOOTSTRAP_YML) run xos_bootstrap_ui python /opt/xos/tosca/run.py None /opt/xos/onboard/vrouter/vrouter-onboard.yaml
	sudo docker-compose -p $(DOCKER_PROJECT) -f $(BOOTSTRAP_YML) run xos_bootstrap_ui python /opt/xos/tosca/run.py None /opt/xos/onboard/volt/volt-onboard.yaml
	sudo docker-compose -p $(DOCKER_PROJECT) -f $(BOOTSTRAP_YML) run xos_bootstrap_ui python /opt/xos/tosca/run.py None /opt/xos/onboard/vsg/vsg-onboard.yaml
	sudo docker-compose -p $(DOCKER_PROJECT) -f $(BOOTSTRAP_YML) run xos_bootstrap_ui python /opt/xos/tosca/run.py None /opt/xos/configurations/common/enable-onboarding.yaml
	bash ../common/wait_for_onboarding_ready.sh 9998 services/vrouter
	bash ../common/wait_for_onboarding_ready.sh 9998 services/volt
	bash ../common/wait_for_onboarding_ready.sh 9998 services/vsg
	bash ../common/wait_for_onboarding_ready.sh 9998 xos
	bash ../common/wait_for_xos_port.sh 9999

restore-initial-db-status:
	sudo docker exec teststandalone_xos_db_1 psql -U postgres -d xos -c "$$TRUNCATE_FN" >/dev/null 2>&1
	sudo docker exec teststandalone_xos_db_1 psql -U postgres -d xos -c "SELECT truncate_tables('postgres');" >/dev/null 2>&1
	sudo docker exec teststandalone_xos_db_1 psql -U postgres -d xos -c "SELECT setval('core_tenant_id_seq', 1)" >/dev/null 2>&1
	sudo docker exec teststandalone_xos_db_1 psql -U postgres -d xos -c "SELECT setval('core_deployment_id_seq', 1)" >/dev/null 2>&1
	sudo docker exec teststandalone_xos_db_1 psql -U postgres -d xos -c "SELECT setval('core_flavor_id_seq', 1)" >/dev/null 2>&1
	sudo docker exec teststandalone_xos_db_1 psql -U postgres -d xos -c "SELECT setval('core_service_id_seq', 1)" >/dev/null 2>&1
	sudo docker-compose run xos python /opt/xos/manage.py --noobserver --nomodelpolicy loaddata /opt/xos/core/fixtures/core_initial_data.json
	sudo docker-compose run xos python /opt/xos/tosca/run.py none /opt/xos/configurations/common/fixtures.yaml
	sudo docker-compose run xos python /opt/xos/tosca/run.py none /opt/xos/configurations/common/mydeployment.yaml
	sudo docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/frontend/sample.yaml


test: restore-initial-db-status
	# RUN TESTS
	sudo docker cp ../../../apiary.apib teststandalone_xos_1:/opt/xos/tests/api/apiary.apib
	sudo docker exec -i teststandalone_xos_1 bash -c "cd /opt/xos/tests/api; npm test"

test-tosca: restore-initial-db-status
	sudo docker-compose run xos bash -c "cd /opt/xos/tosca/tests; python ./alltests.py"

base-container: 
	cd ../../../containers/xos; make base

devel-container: base-container
	cd ../../../containers/xos; make devel

containers: devel-container
	cd ../../../containers/xos; make test

stop:
	sudo docker-compose stop

showlogs:
	sudo docker-compose logs

rm: stop
	sudo docker-compose rm -f

docker-clean:
	sudo docker rm -f $(shell sudo docker ps -aq)

enter-xos:
	sudo docker exec -ti teststandalone_xos_1 bash

enter-xos-db:
	sudo docker exec -ti teststandalone_xos_db_1 bash
