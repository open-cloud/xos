MYIP:=$(shell hostname -i)
RUNNING_CONTAINER=$(shell sudo docker ps|grep "xos"|awk '{print $$NF}')
LAST_CONTAINER=$(shell sudo docker ps -l -q)
XOS_FOLDER=$(shell pwd)

all: frontend

frontend:
	sudo apt-get -y install httpie
	cat ../common/Dockerfile.common Dockerfile.frontend > Dockerfile
	cd ../../..; sudo docker build -t xos -f xos/configurations/frontend/Dockerfile .
	sudo docker run -v $(XOS_FOLDER)/../../core/xoslib:/opt/xos/core/xoslib -p 9999:8000 --add-host="0.0.0.0:127.0.0.1" xos
	bash ../common/wait_for_xos.sh
	echo $(RUNNING_CONTAINER)

interactive:
	cat ../common/Dockerfile.common Dockerfile.frontend > Dockerfile
	cd ../../..; sudo docker build -t xos -f xos/configurations/frontend/Dockerfile .
	echo "Inside the container run: /usr/bin/make -C /opt/xos/configurations/frontend -f Makefile.inside"
	sudo docker run -it -v $(shell pwd)/../..:/opt/xos -p 9999:8000 --add-host="0.0.0.0:127.0.0.1" xos

stop:
	sudo docker stop $(RUNNING_CONTAINER)

start:
	sudo docker start $(LAST_CONTAINER)

showlogs:
	sudo docker logs $(LAST_CONTAINER)

enter:
	sudo docker exec -t -i $(RUNNING_CONTAINER) bash
