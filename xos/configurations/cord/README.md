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
             olt                 virtualbng
             ----                  ----
             ONOS                  ONOS
              |                     |
client ----> CPqD ----> vCPE ----> OvS ----> Internet
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
ctl:~$ git clone https://github.com/open-cloud/xos.git
ctl:~$ cd xos/xos/configurations/cord/
ctl:~/xos/xos/configurations/cord$ make
```

Running `make` in this directory creates the XOS Docker container and runs the TOSCA engine with `cord.yaml` to
configure XOS with the CORD services.  In addition, a number of VMs are created:

1. *Slice mysite_onos*: runs the ONOS Docker container with `virtualbng` app loaded
1. *Slice mysite_onos*: runs the ONOS Docker container with `olt` app loaded
1. *Slice mysite_vbng*: for running OvS with the `virtualbng` app as controller
1. *Slice mysite_volt*: for running OvS with the `olt` app as controller
1. *Slice mysite_clients*: a subscriber client for end-to-end testing
1. *Slice mysite_vcpe*: runs the vCPE Docker container

Once all the VMs are up and the ONOS apps are configured, XOS should be able to get an address mapping from the `virtualbng`
ONOS app for the vCPE. To verify that it has received an IP address mapping, look at the **Routeable subnet:** field in 
the appropriate *Vbng tenant* object in XOS.  It should contain an IP address in the 10.254.0.0/24 subnet.

After launching the ONOS apps, it is necessary to configure software switches along the dataplane so that ONOS can control
them.  To do this, from the `cord` configuration directory:
```
ctl:~/xos/xos/configurations/cord$ cd dataplane/
ctl:~/xos/xos/configurations/cord/dataplane$ ./gen-inventory.sh > hosts
ctl:~/xos/xos/configurations/cord/dataplane$ ansible-playbook -i hosts dataplane.yaml
```

To setup the dataplane for containers on bare metal, perform these steps in addition to the above (note: make sure to sudo when running the playbook):
```
ctl:~/xos/xos/configurations/cord/dataplane$ ./generate-bm.sh > hosts-bm   
ctl:~/xos/xos/configurations/cord/dataplane$ sudo ansible-playbook -i hosts-bm dataplane-bm.yaml
```

The vCPE container that's created by the configuration will be broken because it was started before the dataplane
was setup, and therefore there was no br-lan for it to use with its interfaces. 

To fix this for containers on bare metal, SSH to the compute node that is hosting the vCPE container and run:
```
cp-2:$ service container-mysite_vcpe-1 start
```

Currently the vOLT switch is not forwarding ARP and so it is necessary to set up ARP mappings between the client
and vCPE.  Log into the client and add an ARP entry for the vCPE: 
```
client:$ sudo arp -s 192.168.0.1 <mac-of-eth1-in-vCPE-container>
```
Inside the vCPE container add a similar entry for the client:
```
vcpe:$ arp -s 192.168.0.2 <mac-of-br-sub-on-client>
```

Now SSH into ONOS running the OLT app (see below) and activate the subscriber:
```
onos> add-subscriber-access of:0000000000000001 1 432
```

At this point you should be able to ping 192.168.0.1 from the client.  The final step is to set the 
vCPE as the gateway on the client:
```
client:$ sudo route del default gw 10.11.10.5
client:$ sudo route add default gw 192.168.0.1
```
The client should now be able to surf the Internet through the dataplane.

## Setting up /etc/hosts

To make it easy to log into the various VMs that make up the dataplane, add entries for them into `/etc/hosts` on the 
*ctl* node.  As root, run:
```
ctl:~/xos/xos/configurations/cord/dataplane$ ./gen-etc-hosts.sh >> /etc/hosts
```
For example, to log into the client:
```
ctl:~$ ssh ubuntu@client
```

## How to log into ONOS

ONOS apps are run inside Docker containers hosted in VMs.  All ports exposed by the ONOS container are forwarded to the 
outside, and can be accessed from the *ctl* node over the `flat-lan-1-net` network.  Assuming that `/etc/hosts`
has been configured as described above, it is possible to SSH to the ONOS running the `virtualbng` app as follows (password is *karaf*):

```
$ ssh -p 8101 karaf@onos_vbng
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

## Troubleshooting

#### Problem: No external connectivity from vCPE container
1. Make sure the hosts listed in `virtualbng.json` are the actual compute nodes used in your experiment.
2. Try rebooting the ONOS container running the `virtualbng` app: `$ ssh ubuntu@onos-vbng "sudo docker restart ONOS"`
