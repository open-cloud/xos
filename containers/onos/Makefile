IMAGE_NAME:=xosproject/onos-fork
CONTAINER_NAME:=onos-fork
NO_DOCKER_CACHE?=false

BUILD_ARGS =
ifdef http_proxy
BUILD_ARGS += --build-arg http_proxy=${http_proxy}
endif
ifdef https_proxy
BUILD_ARGS += --build-arg https_proxy=${https_proxy}
endif

.PHONY: build
build: ; sudo docker build --no-cache=${NO_DOCKER_CACHE} --rm -t ${IMAGE_NAME} ${BUILD_ARGS} .

.PHONY: run
run: ; sudo docker run -d --name ${CONTAINER_NAME} ${IMAGE_NAME}

.PHONY: stop
stop: ; sudo docker stop ${CONTAINER_NAME}

.PHONY: rm
rm: ; sudo docker rm ${CONTAINER_NAME}
