.PHONY: build
build: ; docker build --rm -t opencloud .

.PHONY: run
run: ; docker run --rm -d -e TOSCA_CONFIG_PATH=$TOSCA_CONFIG_PATH --name opencloud_server opencloud

.PHONY: stop
stop: ; docker stop opencloud_server

.PHONY: rmcontainer
rmcontainer: ; docker rm opencloud_server
