CONTAINER_NAME:=observer-server

.PHONY: build
build: ; docker build --rm -t observer .

.PHONY: run
run: ; docker run --rm --name ${CONTAINER_NAME} observer

.PHONY: stop
stop: ; docker stop ${CONTAINER_NAME}

.PHONY: rm
rm: ; docker rm ${CONTAINER_NAME}
