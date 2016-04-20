IMAGE_NAME:=xosproject/xos-openvpn
CONTAINER_NAME:=xos-synchronizer
NO_DOCKER_CACHE?=true

.PHONY: build
build: ; sudo docker build --no-cache=${NO_DOCKER_CACHE} --rm -t ${IMAGE_NAME} .

.PHONY: run
run: ; sudo docker run -d --name ${CONTAINER_NAME} -v /usr/local/share/ca-certificates:/usr/local/share/ca-certificates:ro ${IMAGE_NAME}

.PHONY: stop
stop: ; sudo docker stop ${CONTAINER_NAME}

.PHONY: rm
rm: ; sudo docker rm ${CONTAINER_NAME}

.PHONY: rmi
rmi: ; docker rmi ${IMAGE_NAME}
