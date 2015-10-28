RUNNING_CONTAINER:=$(shell sudo docker ps|grep "opencloud-server"|awk '{print $$NF}')

.PHONY: build
build: ; docker build --rm -t opencloud .

.PHONY: run
run: ; docker run --rm  --name opencloud-server -p 80:8000 opencloud

.PHONY: runtosca
runtosca: ; docker exec -it $RUNNING_CONTAINER /usr/bin/python /opt/xos/tosca/run.py padmin@vicci.org $TOSCA_CONFIG_PATH

.PHONY: stop
stop: ; docker stop opencloud-server

.PHONY: rmcontainer
rmcontainer: ; docker rm opencloud-server
