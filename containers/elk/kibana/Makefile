.PHONY: build
build: ; docker build --rm -t kibana .

.PHONY: run
run: ; docker run -d --link elasticsearch_server:elasticsearch -p 8000:80 -e KIBANA_SECURE=false --name kibana_server kibana

.PHONY: runsecure
runsecure: ; docker run -d --link elasticsearch_server:elasticsearch -p 5601:80  --name kibana_server kibana

.PHONY: stop
stop: ; docker stop kibana_server

.PHONY: rmcontainer
rmcontainer: ; docker rm kibana_server
