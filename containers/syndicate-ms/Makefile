IMAGE_NAME:=xosproject/syndicate-ms
CONTAINER_NAME:=xos-syndicate-ms
NO_DOCKER_CACHE?=false

.PHONY: build
build: ; docker build --no-cache=${NO_DOCKER_CACHE} --rm -t ${IMAGE_NAME} .

.PHONY: run
run: ; docker run -d -p 8080:8080 --name ${CONTAINER_NAME} ${IMAGE_NAME}

.PHONY: stop
stop: ; docker stop ${CONTAINER_NAME}

.PHONY: rm
rm: ; docker rm ${CONTAINER_NAME}

.PHONY: rmi
rmi: ; docker rmi ${IMAGE_NAME}

