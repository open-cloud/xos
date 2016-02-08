.PHONY: xos
xos: nodes.yaml images.yaml
	sudo docker-compose up -d
	../xos/configurations/common/wait_for_xos_port.sh 8000
	sudo docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /root/setup/setup.yaml
	sudo docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /root/setup/nodes.yaml
	sudo docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /root/setup/images.yaml

nodes.yaml:
	export SETUPDIR=.; bash ../xos/configurations/common/make-nodes-yaml.sh

images.yaml:
	export SETUPDIR=.; bash ../xos/configurations/common/make-images-yaml.sh

.PHONY: local_containers
local_containers:
	cd containers/xos; make devel
	cd containers/synchronizer; make
