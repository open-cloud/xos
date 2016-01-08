SETUPDIR:=../setup
MYIP:=$(shell hostname -i)

cloudlab: common_cloudlab cord

devstack: upgrade_pkgs common_devstack devstack_net_fix cord

cord: ceilometer_dashboard virtualbng_json vtn_network_cfg_json
	sudo MYIP=$(MYIP) docker-compose up -d
	bash ../common/wait_for_xos.sh
	sudo MYIP=$(MYIP) docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/common/fixtures.yaml
	sudo MYIP=$(MYIP) docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/common/base.yaml
	sudo MYIP=$(MYIP) docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /root/setup/nodes.yaml
	sudo MYIP=$(MYIP) docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/cord/cord.yaml
	sudo MYIP=$(MYIP) docker-compose run xos python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/configurations/cord/ceilometer.yaml

common_cloudlab:
	make -C ../common -f Makefile.cloudlab

common_devstack:
	make -C ../common -f Makefile.devstack

ceilometer_dashboard:
	#NOTE: The below dashboard install scripts assume
	#clouldlab openstack environment created using "OpenStack" profile
	#bash install_xos_ceilometer_dashboard.sh
	bash install_ceilometer_patch.sh

virtualbng_json:
	export SETUPDIR=$(SETUPDIR); bash make-virtualbng-json.sh

vtn_network_cfg_json:
	export SETUPDIR=$(SETUPDIR); bash make-vtn-networkconfig-json.sh

stop:
	sudo MYIP=$(MYIP) docker-compose stop

rm:
	sudo MYIP=$(MYIP) docker-compose rm

showlogs:
	sudo MYIP=$(MYIP) docker-compose logs

ps:
	sudo MYIP=$(MYIP) docker-compose ps

dataplane: etc_hosts
	cd dataplane; ./gen-inventory.sh > hosts
	cd dataplane; ansible-playbook -i hosts dataplane.yaml

dataplane_bm: dataplane
	cd dataplane; bash -c "./generate-bm.sh > hosts-bm"
	cd dataplane; sudo bash -c "ansible-playbook -i hosts-bm dataplane-bm.yaml"

etc_hosts:
	sudo bash -c "sed -i '/^10.11.10/ d' /etc/hosts"
	cd dataplane; sudo bash -c "./gen-etc-hosts.sh >> /etc/hosts"

setup_client:
	# add subscriber to vOLT?  Is there a REST API?
	echo "Don't forget: add-subscriber-access of:0000000000000001 1 432"
	cd dataplane; ansible -i hosts client -m shell -s -a "route del default gw 10.11.10.5; dhclient br-sub"
	# reboot the vBNG ONOS
	cd dataplane; ansible -i hosts onos_vbng -m shell -s -a "docker restart ONOS"

cleanup: stop rm
	cd dataplane; ./cleanup.sh
	bash -c "source ../setup/admin-openrc.sh; nova list --all-tenants; neutron net-list"
	echo "Don't forget to clean up vCPE containers"

devstack_net_fix:
	sudo ../common/devstack/net-fix.sh
	sudo bash -c "source ../setup/admin-openrc.sh; neutron subnet-update private-subnet --dns-nameservers list=true 8.8.8.8 8.8.4.4"

upgrade_pkgs:
	sudo pip install httpie --upgrade
