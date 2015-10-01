MYIP:=$(shell hostname -i)
EXISTING_CONTAINER:=$(shell sudo docker ps|grep "xos"|awk '{print $$NF}')

test: common_cloudlab
	cat ../common/Dockerfile.common Dockerfile.develserver > Dockerfile
	cd ../../..; sudo docker build -t xos -f xos/configurations/develserver/Dockerfile .
	sudo docker run -d --add-host="0.0.0.0:$(MYIP)" -p 9999:8000 xos
	bash ../common/wait_for_xos.sh

common_cloudlab:
	make -C ../common -f Makefile.cloudlab

stop:
	sudo docker stop $(EXISTING_CONTAINER)
