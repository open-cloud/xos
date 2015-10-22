# CORD development environment

This configuration can be used to set up a CORD development environment.
It does the following:

* Sets up a basic dataplane for testing end-to-end packet flow between a subscriber client and the Internet
* Brings up ONOS apps for controlling the dataplane: virtualbng, olt
* Configures XOS with the CORD services: vCPE, vBNG, vOLT

**NOTE:** This configuration is under **active development** and is not yet finished!  Some features are not
fully working yet.

## End-to-end dataplane

The configuration uses XOS to set up an end-to-end dataplane for development of the XOS services and ONOS apps 
used in CORD.  It abstracts away most of the complexity of the CORD hardware using virtual networks
and Open vSwitch (OvS) switches.  At a high level the dataplane looks like this:

```
             olt                virtualbng
             ----                 ----
             ONOS                 ONOS
              |                    |
client ----> OvS ----> vCPE ----> OvS ----> Internet
         1         2          3         4
```

On the datapath are two OvS switches, controlled by the `olt` and `virtualbng` ONOS applications.  Once all the pieces are in
place, the client at left should be able to obtain an IP address via DHCP from the vCPE and send packets out to the Internet.

All of the components in the above diagram (i.e., client, OvS switches, ONOS, and vCPE) currently run in distinct VMs
created by XOS.  The numbers in the diagram correspond to networks set up by XOS:

1. subscriber_network
2. lan_network
3. wan_network
4. public_network

## How to run it

The configuration is intended to be run on [CloudLab](http://cloudlab.us).
It launches an XOS container on Cloudlab that runs the XOS develserver.  The container is left running in the background.

To get started on CloudLab:
* Create an experiment using the *OpenStack-CORD* profile.  (You can also use the *OpenStack* profile, but choose *Kilo*
and disable security groups.)
* Wait until you get an email from CloudLab with title "OpenStack Instance Finished Setting Up".
* Login to the *ctl* node of your experiment and run:
```
$ git clone https://github.com/open-cloud/xos.git
$ cd xos/xos/configurations/cord/
$ make
```

Running `make` in this directory creates the XOS Docker container and runs the TOSCA engine with `cord.yaml` to
configure XOS with the CORD services.  In addition, a number of VMs are created:

1. *Slice mysite_onos*: runs the ONOS Docker container with `virtualbng` app loaded
1. *Slice mysite_onos*: runs the ONOS Docker container with `olt` app loaded
1. *Slice mysite_vbng*: for running OvS with the `virtualbng` app as controller
1. *Slice mysite_volt*: for running OvS with the `olt` app as controller
1. *Slice mysite_clients*: a subscriber client for end-to-end testing

Once all the VMs are up and the ONOS apps are configured, XOS should be able to get an address mapping from the `virtualbng`
ONOS app when creating a vCPE.  To test this, enter the XOS Docker container and run:

```
$ cd /opt/xos/configurations/cord/
$ make -f Makefile.inside setup_subscriber
```

This will run the TOSCA engine with `subscriber.yaml`.  After a bit, a new VM should be created in slice *mysite_vcpe* running
the vCPE Docker container.  To verify that it has received an IP address mapping, look at the **Routeable subnet:** field in 
the appropriate *Vbng tenant* object in XOS.  It should contain an IP address in the 10.254.0.0/24 subnet.

## How to log into ONOS

The ONOS Docker container runs in the VMs belonging to the *mysite_onos* slice.  All ports exposed by the ONOS container are forwarded to the outside, and can be accessed from the *ctl* node using the `flat-lan-1-net` address of the hosting VM.  For example, if the IP addresss of the VM is 10.11.10.30, then it is possible to SSH to ONOS as follows (password is *karaf*):

```
$ ssh -p 8101 karaf@10.11.10.30
Password authentication
Password:
Welcome to Open Network Operating System (ONOS)!
     ____  _  ______  ____
    / __ \/ |/ / __ \/ __/
   / /_/ /    / /_/ /\ \
   \____/_/|_/\____/___/


Hit '<tab>' for a list of available commands
and '[cmd] --help' for help on a specific command.
Hit '<ctrl-d>' or type 'system:shutdown' or 'logout' to shutdown ONOS.

onos>
```

For instance, to check the IP address mappings managed by the `virtualbng` app:

```
onos> vbngs
   Private IP - Public IP
   10.0.1.3 - 10.254.0.129
```
