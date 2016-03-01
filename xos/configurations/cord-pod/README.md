# XOS Configuration for CORD development POD

## Introduction

This directory holds files that are used to configure a development POD for
CORD.  For more information on the CORD project, check out
[the CORD website](http://cord.onosproject.org/).

XOS is composed of several core services:

  * A database backend (postgres)
  * A webserver front end (django)
  * A synchronizer daemon that interacts with the openstack backend
  * A synchronizer for each configured XOS service

Each service runs in a separate Docker container.  The containers are built
automatically by [Docker Hub](https://hub.docker.com/u/xosproject/) using
the HEAD of the XOS repository.

## How to bring up CORD

Installing a CORD POD involves these steps:
 1. Install OpenStack on a cluster
 2. Set up the ONOS VTN app and configuring OVS on the nova-compute nodes to be
    controlled by VTN
 3. Set up external connectivity for VMs (if not using the CORD fabric)
 4. Bring up XOS with the CORD services

### Install OpenStack

Follow the instructions in the [README.md](https://github.com/open-cloud/openstack-cluster-setup/blob/master/README.md)
file of the [open-cloud/openstack-cluster-setup](https://github.com/open-cloud/openstack-cluster-setup/)
repository.

### Set up ONOS VTN

The OpenStack installer above creates a VM called *onos-cord* on the head node.
To bring up ONOS in this VM, log into the head node and run:
```
$ ssh ubuntu@onos-cord
ubuntu@onos-cord:~$ cd cord; sudo docker-compose up -d
```

### Set up external connectivity for VMs

The CORD fabric is responsible for providing external (Internet) connectivity
for VMs created on CORD.  If you are running on CloudLab (or another development
environment) and want external connectivity without the fabric, download [this script](https://raw.githubusercontent.com/open-cloud/openstack-cluster-setup/master/scripts/compute-ext-net.sh)
 and run it as root:
 ```
 $ sudo compute-ext-net.sh
 ```

The script creates a bridge (*databr*) on the node as well as a veth pair
(*veth0/veth1*).  The *veth0* interface is added as a port on *databr* and
VTN is configured to use *veth1* as its data plane interface.  Traffic coming
from *databr* is NAT'ed to the external network via `iptables`.  The configuration
assumes that *databr* assumes the MAC address of *veth0* when it is added as a port
-- this seems to always be the case (though not sure why).

Note that setting up the full fabric is beyond the scope of this README.

### Bringing up XOS

The OpenStack installer above creates a VM called *xos* on the head node.
To bring up XOS in this VM, first log into the head node and run:
```
$ ssh ubuntu@xos
ubuntu@xos:~$ cd xos/xos/configurations/cord-pod
```

Next, check that the following files exist in this directory:

 * *admin-openrc.sh*: Admin credentials for your OpenStack cloud
 * *id_rsa[.pub]*: A keypair that will be used by the various services
 * *node_key*: A private key that allows root login to the compute nodes

They will have been put there for you by the cluster installation scripts.

If your setup uses the CORD fabric, you need to edit `make-vtn-networkconfig-json.sh`
and `cord-vtn-vsg.yml` as appropriate.  Specifically, in
`make-vtn-networkconfig-json.sh` you need to set these parameters for VTN:
 * gatewayIp
 * gatewayMac
 * PHYPORT

And in `cord-vtn-vsg.yml`:
 * public_addresses -> properties -> addresses
 * service_vsg -> properties -> wan_container_gateway_ip
 * service_vsg -> properties -> wan_container_gateway_mac
 * service_vsg -> properties -> wan_container_netbits

If you're not using the fabric then the default values should be OK.  

XOS can then be brought up for CORD by running a few 'make' commands:
```
ubuntu@xos:~/xos/xos/configurations/cord-pod$ make
ubuntu@xos:~/xos/xos/configurations/cord-pod$ make vtn
ubuntu@xos:~/xos/xos/configurations/cord-pod$ make cord
```

After the first 'make' command above, you will be able to login to XOS at
*http://xos/* using username/password `padmin@vicci.org/letmein`.
