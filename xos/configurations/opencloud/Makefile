CONTAINER_NAME:=opencloud-server
TOSCA_CONFIG_PATH:=/opt/xos/configurations/opencloud/opencloud.yaml

.PHONY: build
build: ; docker build --rm -t opencloud .

.PHONY: run
run: ; docker run --rm  --name ${CONTAINER_NAME} -p 80:8000 opencloud

.PHONY: runtosca
runtosca: ; docker exec -it ${CONTAINER_NAME} /usr/bin/python /opt/xos/tosca/run.py padmin@vicci.org ${TOSCA_CONFIG_PATH}

.PHONY: stop
stop: ; docker stop ${CONTAINER_NAME}

.PHONY: rmcontainer
rmcontainer: ; docker rm ${CONTAINER_NAME}
