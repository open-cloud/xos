vtn notes:

see also: https://github.com/hyunsun/documentations/wiki/Neutron-ONOS-Integration-for-CORD-VTN#onos-setup

VTN doesn't seem to like cloudlab's networks (flat-net-1, ext-net, etc). I've placed a script in xos/scripts/ called destroy-all-networks.sh that will automate tearing down all of cloudlab's neutron networks.

    cd xos/scripts
    ./destroy-all-networks.sh

inside the xos container, update the configuration. Make sure to restart Openstack Synchronizer afterward. Might be a good idea to restart the XOS UI as well:

    python /opt/xos/tosca/run.py padmin@vicci.org /opt/xos/tosca/samples/vtn.yaml
    emacs /opt/xos/xos_configuration/xos_common_config
        [networking]
        use_vtn=True
    supervisorctl restart observer

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
    [onos]
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

Compute nodes and nm nodes:

    cd xos/configurations/cord/dataplane
    ./generate-bm.sh > hosts-bm
    ansible-playbook -i hosts-bm dataplane-vtn.yaml
    # the playbook will:
    #  1) turn off neutron openvswitch-agent
    #  2) set openvswitch to listen on port 6641
    #  3) restart openvswitch
    #  4) delete any existing br-int bridge
    #  5) [nm only] turn off neutron-dhcp-agent

Additional compute node stuff:

Br-flat-lan-1 needs to be deleted, since VTN will be attaching br-int directly to the eth device that br-flat-lan-1 was using. Additionally, we need to assign an IP address to br-int (sounds like Hyunsun is working on having VTN do that for us). Adding the route was not in Hyunsun's instructions, but I found I had to do it in order to get the compute nodes to talk to one another.

    ovs-vsctl del-br br-tun
    ovs-vsctl del-br br-flat-lan-1
    ip addr add <addr-that-was-assinged-to-flat-lan-1> dev br-int
    ip link set br-int up
    ip route add <network-that-was-assigned-to-flat-lan-1> dev br-int
    
For development, I suggest using the bash configuration (remember to start the ONOS observer manually) so that 
there aren't a bunch of preexisting Neutron networks and nova instances to get in the way. 

Notes:
* I've configured the OpenvSwitch switches to use port 6641 instead of port 6640. This is because the VTN app listens on 6640
itself, and since we're running it in docker 'host' networking mode now, it would conflict with an Openvswitch that was
also listening on 6640.
* Adding use_vtn=True to the [networking] section in the XOS config file has two effects: 1) it sets the gateway in sync_controller_networks, and 2) it disables automatic creation of nat-net for new slices. This is because VTN will fail if there is no gateway on a network, and because we don't have nat-net under the VTN configuration.
* When using of-vfctl to look at flow rules, if you get a protocol error, try "ovs-ofctl show -O OpenFlow13 br-int "
* Note that the VTN Synchronizer isn't started automatically. It's only use for inter-Service connectivity, so no need to mess with it until intra-Slice connectivity is working first. 
* Note that the VTN Synchronizer won't connect non-access networks. Any network templates you want VTN to connect must have Access set to "Direct" or "Indirect". 

There is no management network yet, so no way to SSH into the slices. I've been setting up a VNC tunnel, like this:

    # on compute node, run the following and note the IP address and port number
    virsh vncdisplay <instance-id>
    
    # from home
    ssh -o "GatewayPorts yes"  -L <port+5900>:<IP>:<port+5900> <username>@<compute_node_hostname>
    
    # example
    ssh -o "GatewayPorts yes"  -L 5901:192.168.0.7:5901 smbaker@cp-1.smbaker-xos3.xos-pg0.clemson.cloudlab.us

Then open a VNC session to the local port on your local machine. You'll have a console on the Instance. The username is "Ubuntu" and the password can be obtained from your cloudlab experiment description

Things that can be tested:

* Create an Instance, it should have a Private network, and there should be a tap attached from the instance to br-int
* Two Instances in the same Slice can talk to one another. They can be on the same machine or different machines.
* Two Slices can talk to one another if the slices are associated with Services and those Services have a Tenancy relationship between them. Note that 1) The VTN Synchronizer must be running, 2) There must be a Private network with Access=[Direct|Indirect], and 3) The connectivity is unidirectional, from subscriber service to provider service.

Testing service composition

1. Change the private network template's 'Access' field from None to Direct
2. Create a Service, Service-A
3. Enter Slice Admin for Slice-1 and assign it to Service-A
4. Create a Service, Service-B
5. Enter Slice Admin for Slice-2 and assign it to Service-B
6. Enter Service Admin for Service-B, Go to Tenancy Tab
7. In the 'Provided Tenants' section of Service-B, create a Tenant with Subsciber-Service=Serivce-A. 
8. Start the VTN Observer. It will send a REST request to VTN app.
9. Launch tcpdump in one of Slice-2's instances
10. From Slice-1, start pinging the instance in Slice-2 where you launched tcpdump
11. You should see the pings arrive and responses sent out. Note that the ping responses will not reach Slice-1, since VTN traffic is unidirectional.
12. Delete the Tenancy relation you created in Step #7. The ping traffic should no longer appear in the tcpdump.

