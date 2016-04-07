MYIP:=$(shell hostname -i)

test: frontend
	# MOCK CORD
	# MOVE THIS TO FIXTURES inside dredd hooks
	#sudo docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/common/fixtures.yaml
	#sudo docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/frontend/mocks/cord.yaml
	
	# INSTALL DEPS
	sudo docker exec -i teststandalone_xos_1 bash -c "cd /opt/xos/tests/api; npm install --production"
	sudo docker exec teststandalone_xos_1 pip install dredd_hooks
	
	# RUN TESTS
	sudo docker exec -i teststandalone_xos_1 bash -c "cd /opt/xos/tests/api; npm test"

frontend:
	sudo make -f ../common/Makefile.prereqs
	sudo docker-compose up -d
	bash ../common/wait_for_xos.sh
	sudo docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/frontend/sample.yaml

base-container: 
	cd ../../../containers/xos; make devel

containers: base-container
	cd ../../../containers/xos; make test

stop:
	sudo docker-compose stop

showlogs:
	sudo docker-compose logs

rm: stop
	sudo docker-compose rm

enter-xos:
	sudo docker exec -ti teststandalone_xos_1 bash

enter-xos-db:
	sudo docker exec -ti teststandalone_xos_db_1 bash
