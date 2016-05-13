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

To set up OpenStack, follow the instructions in the
[README.md](https://github.com/open-cloud/openstack-cluster-setup/blob/master/README.md)
file of the [open-cloud/openstack-cluster-setup](https://github.com/open-cloud/openstack-cluster-setup/)
repository.  If you're just getting started with CORD, it's probably best to begin with the
single-node CORD test environment to familiarize yourself with the overall setup.

**NOTE: In order to use the cord-pod configuration, you must set up OpenStack using the above recipe.**

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
 and run it on the Nova compute node(s) as root:
 ```
 $ sudo compute-ext-net.sh
 ```

The script creates a bridge (*databr*) on the node as well as a veth pair
(*veth0/veth1*).  The *veth0* interface is added as a port on *databr* and
VTN is configured to use *veth1* as its data plane interface.  Traffic coming
from *databr* is NAT'ed to the external network via `iptables`.  The configuration
assumes that *databr* takes the MAC address of *veth0* when it is added as a port
-- this seems to always be the case (though not sure why).

Note that setting up the full fabric is beyond the scope of this README.

### Bringing up XOS

The OpenStack installer above creates a VM called *xos* on the head node.
To bring up XOS in this VM, first log into the head node and run:
```
$ ssh ubuntu@xos
ubuntu@xos:~$ cd xos/xos/configurations/cord-pod
```

Next, check that the following files exist in this directory
(they will have been put there for you by the cluster installation scripts):

 * *admin-openrc.sh*: Admin credentials for your OpenStack cloud
 * *id_rsa[.pub]*: A keypair that will be used by the various services
 * *node_key*: A private key that allows root login to the compute nodes

XOS can then be brought up for CORD by running a few `make` commands.
First, run:

```
ubuntu@xos:~/xos/xos/configurations/cord-pod$ make
```

Before proceeding, you should verify that objects in XOS are
being sync'ed with OpenStack. [Login to the XOS GUI](#logging-into-xos-on-cloudlab-or-any-remote-host) 
and select *Users* at left.  Make sure there is a green check next to `padmin@vicci.org`.

> If you are **not** building the single-node development POD, the next
> step is to create and edit the VTN configuration.  Run `make vtn-external.yaml`
> then edit the `vtn-external.yml` TOSCA file.  The `rest_hostname:`
> field points to the host where ONOS should run the VTN app.  The
> fields in the `service_vtn` and the objects of type `tosca.nodes.Tag`
> correspond to the VTN fields listed
> on [the CORD VTN page on the ONOS Wiki](https://wiki.onosproject.org/display/ONOS/CORD+VTN),
> under the **ONOS Settings** heading; refer there for the fields'
> meanings.  

Then run:

```
ubuntu@xos:~/xos/xos/configurations/cord-pod$ make vtn
```
The above step configures the ONOS VTN app by generating a configuration
and pushing it to ONOS.  You are able to see and modify the configuration
via the GUI as follows:

* To see the generated configuration, go to *http://xos/admin/onos/onosapp/* 
([caveat](#logging-into-xos-on-cloudlab-or-any-remote-host)), select
*VTN_ONOS_app*, then the *Attributes* tab, and look for the
`rest_onos/v1/network/configuration/` attribute.  

* To change the VTN configuration, modify the fields of the VTN Service object
and the Tag objects associated with Nodes.  Don't forget to select *Save*.

* After modifying the above fields, delete the `rest_onos/v1/network/configuration/` attribute
in the *ONOS_VTN_app* and select *Save*.  The attribute will be regenerated using the new information.

* Alternatively, if you want to load your own VTN configuration manually, you can delete the
`autogenerate` attribute from the *ONOS_VTN_app*, edit the configuration in the
`rest_onos/v1/network/configuration/` attribute, and select *Save*.

Before proceeding, check that the VTN app is controlling Open vSwitch on the compute nodes.  Log
into ONOS and run the `cordvtn-nodes` command:

```
$ ssh -p 8101 karaf@onos-cord   # password is karaf
onos> cordvtn-nodes
hostname=nova-compute, hostMgmtIp=192.168.122.177/24, dpIp=192.168.199.1/24, br-int=of:0000000000000001, dpIntf=veth1, init=COMPLETE
Total 1 nodes
```
The important part is the `init=COMPLETE` at the end.  If you do not see this, refer to
[the CORD VTN page on the ONOS Wiki](https://wiki.onosproject.org/display/ONOS/CORD+VTN) for
help fixing the problem.  This must be working to bring up VMs on the POD.

> If you are **not** building the single-node development POD, modify `cord-vtn-vsg.yml` 
> and change `addresses_vsg` so that it contains the IP address block,
> gateway IP, and gateway MAC of the CORD fabric.  

Then run:

```
ubuntu@xos:~/xos/xos/configurations/cord-pod$ make cord
```


### Inspecting the vSG

The above series of `make` commands will spin up a vSG for a sample subscriber.  The
vSG is implemented as a Docker container (using the
[andybavier/docker-vcpe](https://hub.docker.com/r/andybavier/docker-vcpe/) image
hosted on Docker Hub) running inside an Ubuntu VM.  Once the VM is created, you
can login as the `ubuntu` user at the management network IP (172.27.0.x) on the compute node
hosting the VM, using the private key generated on the head node by the install process.
For example, in the single-node development POD configuration, you can login to the VM
with management IP 172.27.0.2 using a ProxyCommand as follows:

```
ubuntu@pod:~$ ssh -o ProxyCommand="ssh -W %h:%p ubuntu@nova-compute" ubuntu@172.27.0.2
```

Alternatively, you could copy the generated private key to the compute node
and login from there:

```
ubuntu@pod:~$ scp ~/.ssh/id_rsa ubuntu@nova-compute:~/.ssh
ubuntu@pod:~$ ssh ubuntu@nova-compute
ubuntu@nova-compute:~$ ssh ubuntu@172.27.0.2
```

Once logged in to the VM, you can run `sudo docker ps` to see the running
vSG containers:

```
ubuntu@mysite-vsg-1:~$ sudo docker ps
CONTAINER ID        IMAGE                    COMMAND             CREATED             STATUS              PORTS               NAMES
2b0bfb3662c7        andybavier/docker-vcpe   "/sbin/my_init"     5 days ago          Up 5 days                               vcpe-222-111
```

### Logging into XOS on CloudLab (or any remote host)

The XOS service is accessible on the POD at `http://xos/`, but `xos` maps to a private IP address
on the management network.  If you install CORD on CloudLab 
you will not be able to directly access the XOS GUI.
In order to log into the XOS GUI in the browser on your local machine (desktop or laptop), 
you can set up an SSH tunnel to your CloudLab node.  Assuming that 
`<your-cloudlab-node>` is the DNS name of the CloudLab node hosting your experiment,
run the following on your local machine to create the tunnel:

```
$ ssh -L 8888:xos:80 <your-cloudlab-node>
```

Then you should be able to access the XOS GUI by pointing your browser to
`http://localhost:8888`.  Default username/password is `padmin@vicci.org/letmein`.
