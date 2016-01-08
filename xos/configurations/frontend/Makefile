MYIP:=$(shell hostname -i)
RUNNING_CONTAINER=$(shell sudo docker ps|grep "xos_1"|awk '{print $$NF}')

frontend:
	sudo apt-get -y install httpie
	sudo docker-compose up -d
	bash ../common/wait_for_xos.sh
	sudo docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/frontend/sample.yaml

stop:
	sudo docker-compose stop

showlogs:
	sudo docker-compose logs

rm: stop
	sudo docker-compose rm

ps:
	sudo docker-compose ps

enter:
	sudo docker exec -t -i $(RUNNING_CONTAINER) bash
