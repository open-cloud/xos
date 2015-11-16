CONTAINER_NAME:=synchronizer-server

.PHONY: build
build: ; docker build --rm -t synchronizer .

.PHONY: run
run: ; docker run -d --name ${CONTAINER_NAME} synchronizer

.PHONY: stop
stop: ; docker stop ${CONTAINER_NAME}

.PHONY: rm
rm: ; docker rm ${CONTAINER_NAME}
