# Setting up the XOS Tutorial

The XOS Tutorial demonstrates how to add a new subscriber-facing
service to CORD.  

## Prepare the development POD

Follow steps 1-3 under the **How to Bring up CORD** heading in the
[README.md](./README.md) file.  For best results, use on a clean Ubuntu 14.04
LTS installation on a server with at least 48GB RAM and 12 CPU cores.

For step 1, use the single-node POD setup described at
https://github.com/open-cloud/openstack-cluster-setup.  If you like, you can run
[this script](https://github.com/open-cloud/openstack-cluster-setup/blob/master/scripts/single-node-pod.sh) to perform steps 1 and 2:

```
ubuntu@pod:~$ wget https://raw.githubusercontent.com/open-cloud/openstack-cluster-setup/master/scripts/single-node-pod.sh
ubuntu@pod:~$ bash single-node-pod.sh
```

For step 3, in place of the `compute-ext-net.sh` script, run
[this script](https://github.com/open-cloud/openstack-cluster-setup/blob/master/scripts/compute-ext-net-tutorial.sh)
inside the nova-compute VM.  It enables routing packets between the ExampleService and vSG subnets on a
single-node POD.

```
ubuntu@pod:~$ ssh ubuntu@nova-compute
ubuntu@nova-compute:~$ wget https://raw.githubusercontent.com/open-cloud/openstack-cluster-setup/master/scripts/compute-ext-net-tutorial.sh
ubuntu@nova-compute:~$ sudo bash compute-ext-net-tutorial.sh
```

## Include ExampleService in XOS

On the POD, SSH into the XOS VM: `$ ssh ubuntu@xos`.  You will see the XOS repository
checked out under `~/xos/`

Change the XOS code as described in the
[ExampleService Tutorial](http://guide.xosproject.org/devguide/exampleservice/)
under the **Install the Service in Django** heading, and rebuild the XOS containers as
described in that Tutorial:

```
ubuntu@xos:~$ cd xos/xos/configurations/devel
ubuntu@xos:~/xos/xos/configurations/devel$ make containers
```

Change directories to `../cord-pod`.  
Modify the `docker-compose.yml` file in this directory to include the synchronizer
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

```
xos:
    ...
    volumes:
        ...
        - ./id_rsa.pub:/opt/xos/synchronizers/exampleservice/exampleservice_public_key:ro 
```

## Bring up XOS

Under the `cord-pod` configuration, edit file `make-vtn-networkconfig-json.sh`.
Change the definition of `"publicGateways"` so that it looks like this (adding
  a second gatewayIp and gatewayMac):

```
"publicGateways": [
    {
        "gatewayIp": "10.168.0.1",
        "gatewayMac": "02:42:0a:a8:00:01"
    },
    {
        "gatewayIp": "10.168.1.1",
        "gatewayMac": "02:42:0a:a8:00:01"
    }
],
```

Now run the `make` commands described in the [README.md](./README.md) file:

```
ubuntu@xos:~/xos/xos/configurations/cord-pod$ make
ubuntu@xos:~/xos/xos/configurations/cord-pod$ make vtn
ubuntu@xos:~/xos/xos/configurations/cord-pod$ make cord
```

The first `make` command initializes XOS and configures it to talk to OpenStack.
After running it you should be able to login to the XOS UI at http://xos
using credentials padmin@vicci.org/letmein.

The `make vtn` tells XOS to start and configure the ONOS VTN app.  The `make cord`
installs the CORD services in XOS and configures a sample subscriber; the end
result is that XOS will spin up the subscriber's vSG.

## Configure ExampleService in XOS

The TOSCA file `pod-exampleservice.yaml` contains the service declaration.
Tell XOS to process it by running:

```
ubuntu@xos:~/xos/xos/configurations/cord-pod$ make exampleservice
```

In the XOS UI, create an ExampleTenant. Go to *http://xos/admin/exampleservice*
and add / save an Example Tenant (when creating the tenant, fill in a message that
this tenant should display).  This will cause an Instance to be created
in the the *mysite_exampleservice* slice.

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
