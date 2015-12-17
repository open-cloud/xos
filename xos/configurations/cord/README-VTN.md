vtn notes:

inside the xos container:

    python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/tosca/samples/vtn.yaml

ctl node:

    # set ONOS_VTN_HOSTNAME to the host where the VTN container was installed
    ONOS_VTN_HOSTNAME="cp-2.smbaker-xos5.xos-pg0.clemson.cloudlab.us"
    apt-get install python-pip
    pip install -U setuptools pip
    git clone https://github.com/openstack/networking-onos.git
    cd networking-onos
    sudo python setup.py install
    cat > /usr/local/etc/neutron/plugins/ml2/conf_onos.ini <<EOF
    [ml2_onos]
    url_path = http://$ONOS_VTN_HOSTNAME:8181/onos/vtn
    username = karaf
    password = karaf
    EOF
    emacs /etc/neutron/plugins/ml2/ml2_conf.ini
        update settings as per vtn docs ([ml2] and [ml2_type_vxlan] sections)
    systemctl restart neutron-server

Compute node that has the ONOS Container

    # we need NAT rule so the neutron vtn plugin can talk to onos
    # change 172.17.0.2 to the IP address for the ONOS container (use "docker inspect")
    iptables -t nat -A PREROUTING -i br-ex -p tcp --dport 8101 -j DNAT --to-destination 172.17.0.2

Compute nodes (all of them):

    systemctl stop neutron-plugin-openvswitch-agent
    /usr/share/openvswitch/scripts/ovs-ctl
        update settings as per vtn docs to make port 6640 visible
    service openvswitch-switch restart

VTN doesn't seem to like cloudlab's networks (flat-net-1, ext-net, etc). You might have to delete them all.

For development, I suggest using the bash configuration (remember to start the ONOS observer manually) so that 
there aren't a bunch of preexisting Neutron networks and nova instances to get in the way. 