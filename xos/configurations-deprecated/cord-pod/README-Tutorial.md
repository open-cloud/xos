# Setting up the XOS Tutorial

The XOS Tutorial demonstrates how to add a new subscriber-facing
service to CORD.  

## Prepare the development POD

This tutorial runs on a single-node CORD POD development environment.
For best results, prepare a clean Ubuntu 14.04
LTS installation on a server with at least 48GB RAM and 12 CPU cores.
Update the packages to the latest versions.

To set up the POD, run
[this script](https://github.com/open-cloud/openstack-cluster-setup/blob/master/scripts/single-node-pod.sh)
with the `-e` option:

```
ubuntu@pod:~$ wget https://raw.githubusercontent.com/open-cloud/openstack-cluster-setup/master/scripts/single-node-pod.sh
ubuntu@pod:~$ bash single-node-pod.sh -e
```

> NOTE: The above script can also automatically perform all tutoral steps if run as `bash single-node-pod -e -t`.  

Be patient... it will take **at least one hour** to fully set up the single-node POD.

## Include ExampleService in XOS

On the POD, SSH into the XOS VM: `$ ssh ubuntu@xos`.  You will see the XOS repository
checked out under `~/xos/`

Change the XOS code as described in the
[ExampleService Tutorial](http://guide.xosproject.org/devguide/exampleservice/)
under the **Install the Service in Django** heading, and rebuild the XOS containers as
follows:

```
ubuntu@xos:~$ cd xos/xos/configurations/cord-pod
ubuntu@xos:~/xos/xos/configurations/cord-pod$ make local_containers
```

Modify the `docker-compose.yml` file in the `cord-pod` directory to include the synchronizer
for ExampleService:

```yaml
xos_synchronizer_exampleservice:
    image: xosproject/xos-synchronizer-openstack
    command: bash -c "sleep 120; python /opt/xos/synchronizers/exampleservice/exampleservice-synchronizer.py -C /root/setup/files/exampleservice_config"
    labels:
        org.xosproject.kind: synchronizer
        org.xosproject.target: exampleservice
    links:
        - xos_db
    volumes:
        - .:/root/setup:ro
        - ../common/xos_common_config:/opt/xos/xos_configuration/xos_common_config:ro
        - ./id_rsa:/opt/xos/synchronizers/exampleservice/exampleservice_private_key:ro
```

Also, add ExampleService's public key to the `volumes` section of the `xos` docker container:

```yaml
xos:
    ...
    volumes:
        ...
        - ./id_rsa.pub:/opt/xos/synchronizers/exampleservice/exampleservice_public_key:ro 
```

## Bring up XOS

Run the `make` commands described in the [Bringing up XOS](https://github.com/open-cloud/xos/blob/master/xos/configurations/cord-pod/README.md#bringing-up-xos)
section of the README.md file.

## Configure ExampleService in XOS

The TOSCA file `pod-exampleservice.yaml` contains the service declaration.
Tell XOS to process it by running:

```
ubuntu@xos:~/xos/xos/configurations/cord-pod$ make exampleservice
```

This will add the ExampleService to XOS.  It will also create an ExampleTenant,
which causes a VM to be created with Apache running inside.


## Set up a Subscriber Device

The single-node POD does not include a virtual OLT, but a device at the
subscriber’s premises can be simulated by an LXC container running on the
nova-compute node.

In the nova-compute VM:

```
ubuntu@nova-compute:~$ sudo apt-get install lxc
```

Next edit `/etc/lxc/default.conf` and change the default bridge name to `databr`:

```
  lxc.network.link = databr
```

Create the client container and attach to it:

```
ubuntu@nova-compute:~$ sudo lxc-create -t ubuntu -n testclient
ubuntu@nova-compute:~$ sudo lxc-start -n testclient
ubuntu@nova-compute:~$ sudo lxc-attach -n testclient
```

(The lxc-start command may throw an error but it seems to be unimportant.)

Finally, inside the container set up an interface so that outgoing traffic
is tagged with the s-tag (222) and c-tag (111) configured for the
sample subscriber:

```
root@testclient:~# ip link add link eth0 name eth0.222 type vlan id 222
root@testclient:~# ip link add link eth0.222 name eth0.222.111 type vlan id 111
root@testclient:~# ifconfig eth0.222 up
root@testclient:~# ifconfig eth0.222.111 up
root@testclient:~# dhclient eth0.222.111
```

If the vSG is up and everything is working correctly, the eth0.222.111
interface should acquire an IP address via DHCP and have external connectivity.

## Access ExampleService from the Subscriber Device

To test that the subscriber device can access the ExampleService, find the IP
address of the ExampleService Instance in the XOS GUI, and then curl this
address from inside the testclient container:

```
root@testclient:~# sudo apt-get install curl
root@testclient:~# curl 10.168.1.3
ExampleService
 Service Message: "service_message"
 Tenant Message: "tenant_message"
```

Hooray!  This shows that the subscriber (1) has external connectivity, and
(2) can access the new service via the vSG.

## Troubleshooting

Sometimes the ExampleService instance comes up with the wrong default route.  If the 
ExampleService instance is active but the `curl` command does not work, SSH to the
instance and check its default gateway.  Assuming the management address of the `mysite_exampleservice`
VM is 172.27.0.2:

```
ubuntu@pod:~$ ssh-agent bash
ubuntu@pod:~$ ssh-add
ubuntu@pod:~$ ssh -A ubuntu@nova-compute
ubuntu@nova-compute:~$ ssh ubuntu@172.27.0.2
ubuntu@mysite-exampleservice-2:~$ route -n
Kernel IP routing table
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
0.0.0.0         172.27.0.1      0.0.0.0         UG    0      0        0 eth1
10.168.1.0      0.0.0.0         255.255.255.0   U     0      0        0 eth0
172.27.0.0      0.0.0.0         255.255.255.0   U     0      0        0 eth1
```

If the default gateway is not `10.168.1.1`, manually set it to this value.

```
ubuntu@mysite-exampleservice-2:~$ sudo bash
root@mysite-exampleservice-2:~# route del default gw 172.27.0.1
root@mysite-exampleservice-2:~# route add default gw 10.168.1.1
root@mysite-exampleservice-2:~# route -n
Kernel IP routing table
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
0.0.0.0         10.168.1.1      0.0.0.0         UG    0      0        0 eth0
10.168.1.0      0.0.0.0         255.255.255.0   U     0      0        0 eth0
172.27.0.0      0.0.0.0         255.255.255.0   U     0      0        0 eth1
```

Now the VM should have Internet connectivity and XOS will start downloading Apache. 
A short while later the `curl` test should complete.
