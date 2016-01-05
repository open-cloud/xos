vtn notes:

see also: https://github.com/hyunsun/documentations/wiki/Neutron-ONOS-Integration-for-CORD-VTN#onos-setup

inside the xos container:

    python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/tosca/samples/vtn.yaml

ctl node:

    # set ONOS_VTN_HOSTNAME to the host where the VTN container was installed
    ONOS_VTN_HOSTNAME="cp-2.smbaker-xos5.xos-pg0.clemson.cloudlab.us"
    apt-get -y install python-pip
    pip install -U setuptools pip
    pip install testrepository
    git clone https://github.com/openstack/networking-onos.git
    cd networking-onos
    python setup.py install
    # the above fails the first time with an error about pbr.json
    # I ran it again and it succeeded, but I am skeptical there's
    # not still an issue lurking...
    cat > /usr/local/etc/neutron/plugins/ml2/conf_onos.ini <<EOF
    [ml2_onos]
    url_path = http://$ONOS_VTN_HOSTNAME:8181/onos/openstackswitching
    username = karaf
    password = karaf
    EOF
    emacs /etc/neutron/plugins/ml2/ml2_conf.ini
        update settings as per vtn docs ([ml2] and [ml2_type_vxlan] sections)
    systemctl stop neutron-server
    # I started neutron manually to make sure it's using exactly the right config
    # files. Maybe it can be restarted using systemctl instead...
    /usr/bin/neutron-server --config-file /etc/neutron/neutron.conf --config-file /etc/neutron/plugins/ml2/ml2_conf.ini --config-file /usr/local/etc/neutron/plugins/ml2/conf_onos.ini

Neutron driver arg-parsing issue

    # For some reason, the VTN Neutron plugin isn't getting its arguments from neutron
    emacs /usr/local/lib/python2.7/dist-packages/networking_onos/plugins/ml2/driver.py
        hard-code self.onos_path and self.onos_auth
    
Compute node that has the ONOS Container

    # we need NAT rule so the neutron vtn plugin can talk to onos
    # change 172.17.0.2 to the IP address for the ONOS container (use "docker inspect")
    iptables -t nat -A PREROUTING -i br-ex -p tcp --dport 8101 -j DNAT --to-destination 172.17.0.2
    iptables -t nat -A PREROUTING -i br-ex -p tcp --dport 8181 -j DNAT --to-destination 172.17.0.2

Compute nodes (all of them):

    systemctl stop neutron-plugin-openvswitch-agent
    emacs /usr/share/openvswitch/scripts/ovs-ctl
        update settings as per vtn docs to make port 6640 visible
    service openvswitch-switch restart
    ovs-vsctl del-br br-int

VTN doesn't seem to like cloudlab's networks (flat-net-1, ext-net, etc). You might have to delete them all. I've placed a script in xos/scripts/ called destroy-all-networks.sh that will automate tearing down all of cloudlab's neutron networks.

For development, I suggest using the bash configuration (remember to start the ONOS observer manually) so that 
there aren't a bunch of preexisting Neutron networks and nova instances to get in the way. 

Problems:
* If you have more than one compute node, then the node that isn't running ONOS VTN will report as incomplete in VTN. This is because the openvswitch is trying to contact VTN on 172.17.0.2:6653. 
* VTN doesn't like the nat-net network that XOS creates by default. Go into model_policies/model_policy_Slice.py and disable automatic creation of nat-net.
