.PHONY: build
build: ; docker build --rm -t logstash-forwarder .

.PHONY: run
run: ; docker run --rm -v `pwd`/../logstash/certs:/opt/certs -v /var/log/:/var/log --name logstash-forwarder_server -i -t logstash-forwarder

.PHONY: stop
stop: ; docker stop logstash-forwarder_server 

.PHONY: rmcontainer
rmcontainer: ; docker rm logstash-forwarder_server 
