IMAGE_NAME:=xosproject/onos-fork
CONTAINER_NAME:=onos-fork
NO_DOCKER_CACHE?=false

.PHONY: build
build: ; sudo docker build --no-cache=${NO_DOCKER_CACHE} --rm -t ${IMAGE_NAME} .

.PHONY: run
run: ; sudo docker run -d --name ${CONTAINER_NAME} ${IMAGE_NAME}

.PHONY: stop
stop: ; sudo docker stop ${CONTAINER_NAME}

.PHONY: rm
rm: ; sudo docker rm ${CONTAINER_NAME}
