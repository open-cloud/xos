CONTAINER_NAME:=xos-server
IMAGE_NAME:=xosproject/xos
TOSCA_CONFIG_PATH:=/opt/xos/configurations/opencloud/opencloud.yaml
NO_DOCKER_CACHE?=false

.PHONY: build
build: ; docker build --no-cache=${NO_DOCKER_CACHE} --rm -t ${IMAGE_NAME} . && ./initdb

.PHONY: run
run: ; docker run -d --name ${CONTAINER_NAME} -p 80:8000 ${IMAGE_NAME}

.PHONY: runtosca
runtosca: ; docker exec -it ${CONTAINER_NAME} /usr/bin/python /opt/xos/tosca/run.py padmin@vicci.org ${TOSCA_CONFIG_PATH}

.PHONY: stop
stop: ; docker stop ${CONTAINER_NAME}

.PHONY: rm
rm: ; docker rm ${CONTAINER_NAME}
