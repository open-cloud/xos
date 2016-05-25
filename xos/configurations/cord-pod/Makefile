.PHONY: xos
xos: up bootstrap

up:
	sudo docker-compose up -d
	../common/wait_for_xos_port.sh 80

bootstrap: nodes.yaml images.yaml
	sudo docker-compose run xos python /opt/xos/tosca/run.py none /opt/xos/configurations/common/fixtures.yaml
	sudo docker-compose run xos python /opt/xos/tosca/run.py none /opt/xos/configurations/common/mydeployment.yaml
	sudo docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /root/setup/setup.yaml
	sudo docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /root/setup/nodes.yaml
	sudo docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /root/setup/images.yaml

vtn: vtn-external.yaml
	sudo docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /root/setup/vtn-external.yaml

cord: vsg_custom_images
	sudo docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /root/setup/mgmt-net.yaml
	sudo docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /root/setup/cord-vtn-vsg.yaml

exampleservice:
	sudo docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /root/setup/pod-exampleservice.yaml

cord-ceilometer: ceilometer_custom_images cord
	sudo docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /root/setup/ceilometer.yaml

nodes.yaml:
	export SETUPDIR=.; bash ../common/make-nodes-yaml.sh

images.yaml:
	export SETUPDIR=.; bash ../common/make-images-yaml.sh

vtn-external.yaml:
	export SETUPDIR=.; bash ./make-vtn-external-yaml.sh

virtualbng_json:
	export SETUPDIR=.; bash ./make-virtualbng-json.sh

vtn_network_cfg_json:
	export SETUPDIR=.; bash ./make-vtn-networkconfig-json.sh

stop:
	sudo MYIP=$(MYIP) docker-compose stop

rm:
	sudo MYIP=$(MYIP) docker-compose rm

showlogs:
	sudo MYIP=$(MYIP) docker-compose logs

cleanup: stop rm
	./cleanup.sh
	bash -c "source ./admin-openrc.sh; nova list --all-tenants; neutron net-list"

ceilometer_custom_images: images/ceilometer-trusty-server-multi-nic.img
	bash -c "source ./admin-openrc.sh; glance image-show ceilometer-trusty-server-multi-nic || glance image-create --name ceilometer-trusty-server-multi-nic --disk-format qcow2 --file ./images/ceilometer-trusty-server-multi-nic.img --container-format bare"

vsg_custom_images: images/vsg-1.0.img
	bash -c "source ./admin-openrc.sh; glance image-show vsg-1.0 || glance image-create --name vsg-1.0 --disk-format qcow2 --file ./images/vsg-1.0.img --container-format bare"

images/ceilometer-trusty-server-multi-nic.img: images
	wget http://www.vicci.org/cord/ceilometer-trusty-server-multi-nic.compressed.qcow2 -P ./images
	mv ./images/ceilometer-trusty-server-multi-nic.compressed.qcow2 ./images/ceilometer-trusty-server-multi-nic.img

images/vsg-1.0.img: images
	wget http://www.vicci.org/cord/vsg-1.0.img -P ./images

images:
	mkdir -p ./images

.PHONY: local_containers
local_containers:
	echo "" > ../../../containers/xos/local_certs.crt
	for CRT in /usr/local/share/ca-certificates/* ; do \
		echo Adding Certificate: $$CRT ;\
		cat $$CRT >> ../../../containers/xos/local_certs.crt ;\
		echo "" >> ../../../containers/xos/local_certs.crt ;\
	done
	cd ../../../containers/xos; make devel
	cd ../../../containers/synchronizer; make

