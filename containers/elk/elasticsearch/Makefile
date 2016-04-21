.PHONY: build
build: ; docker build --rm -t elasticsearch .

.PHONY: run
run: ; docker run -d -p 9200:9200 --name elasticsearch_server elasticsearch

.PHONY: stop
stop: ; docker stop elasticsearch_server

.PHONY: rmcontainer
rmcontainer: ; docker rm elasticsearch_server
