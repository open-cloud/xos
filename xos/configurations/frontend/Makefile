MYIP:=$(shell hostname -i)
RUNNING_CONTAINER=$(shell sudo docker ps|grep "xos"|awk '{print $$NF}')
LAST_CONTAINER=$(shell sudo docker ps -l -q)

all: frontend

frontend:
	sudo apt-get -y install httpie
	cat ../common/Dockerfile.common Dockerfile.frontend > Dockerfile
	cd ../../..; sudo docker build -t xos -f xos/configurations/frontend/Dockerfile .
	sudo docker run -d --add-host="0.0.0.0:$(MYIP)" -p 9999:8000 xos
	bash ../common/wait_for_xos.sh

stop:
	sudo docker stop $(RUNNING_CONTAINER)

showlogs:
	sudo docker logs $(LAST_CONTAINER)

enter:
	sudo docker exec -t -i $(EXISTING_CONTAINER) bash