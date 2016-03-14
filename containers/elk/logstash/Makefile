IP=`curl icanhazip.com`
IP=66.228.36.77
SUBJECT="/C=US/ST=NY/O=Internet Widgits Pty Ltd/subjectAltName=IP:${IP}"

.PHONY: certs
certs: ; [ ! -d certs  ] && mkdir certs && cd certs && openssl req -x509 -batch -nodes -newkey rsa:2048 -keyout logstash-forwarder.key -out logstash-forwarder.crt

.PHONY: build
build: ; docker build --rm -t logstash .

.PHONY: run
run: ; docker run -d --link elasticsearch_server:elasticsearch -p 5043:5043 -p 514:514 -v `pwd`/certs:/opt/logstash/certs -v `pwd`/conf:/opt/logstash/conf --name logstash_server -i -t logstash

.PHONY: stop
stop: ; docker stop logstash_server 

.PHONY: rmcontainer
rmcontainer: ; docker rm logstash_server
