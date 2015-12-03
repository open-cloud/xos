IMAGE_NAME:=xosproject/xos-synchronizer-openstack
CONTAINER_NAME:=xos-synchronizer

.PHONY: build
build: ; docker build --rm -t ${IMAGE_NAME} .

.PHONY: run
run: ; docker run -d --name ${CONTAINER_NAME} ${IMAGE_NAME}

.PHONY: stop
stop: ; docker stop ${CONTAINER_NAME}

.PHONY: rm
rm: ; docker rm ${CONTAINER_NAME}
