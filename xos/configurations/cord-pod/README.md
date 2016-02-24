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

Installing a CORD POD requires three steps:
 1. Installing OpenStack on a cluster
 2. Setting up the ONOS VTN app and configuring OVS on the nova-compute nodes to be
    controlled by VTN
 3. Bringing up XOS with the CORD services

### Installing OpenStack

Follow the instructions in the [README.md](https://github.com/open-cloud/openstack-cluster-setup/blob/master/README.md)
file of the [open-cloud/openstack-cluster-setup](https://github.com/open-cloud/openstack-cluster-setup/)
repository.

### Setting up ONOS VTN

The OpenStack installer above creates a VM called *onos-cord* on the head node.
To bring up ONOS in this VM, log into the head node and run:
```
$ ssh ubuntu@onos-cord
ubuntu@onos-cord:~$ cd cord; docker-compose up -d
```

Currently it's also necessary to do some manual configuration on each compute
node.  As root do the following:
 1. Disable neutron-plugin-openvswitch-agent, if running:
```
$ service neutron-plugin-openvswitch-agent stop
$ echo manual > /etc/init/neutron-plugin-openvswitch-agent.override
```
 2. Delete *br-int* and all other bridges from OVS
 3. Configure OVS to listen for connections from VTN:
```
$ ovs-appctl -t ovsdb-server ovsdb-server/add-remote ptcp:6641
```

### Bringing up XOS

The OpenStack installer above creates a VM called *xos* on the head node.
To bring up XOS in this VM, first log into the head node and run:
```
$ ssh ubuntu@xos
ubuntu@xos:~$ cd xos/xos/configurations/cord-pod
```

Next, put the following files in this directory:

 * *admin-openrc.sh*: Admin credentials for your OpenStack cloud
 * *id_rsa[.pub]*: A keypair that will be used by the various services
 * *node_key*: A private key that allows root login to the compute nodes

Then XOS can be brought up for CORD by running a few 'make' commands:
```
ubuntu@xos:~/xos/xos/configurations/cord-pod$ make
ubuntu@xos:~/xos/xos/configurations/cord-pod$ make vtn
ubuntu@xos:~/xos/xos/configurations/cord-pod$ make cord
```

After the first 'make' command above, you will be able to login to XOS at
*http://xos/* using username/password `padmin@vicci.org/letmein`.
