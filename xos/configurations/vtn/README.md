# XOS+VTN development environment

This goal is to use this configuration to do basic end-to-end development of XOS and VTN.  
It launches
XOS in three Docker containers (development GUI, Synchronizer, database) and configures XOS
to talk to an OpenStack backend.  *docker-compose* is used to manage the containers.

See [the VTN README](../cord/README-VTN.md) for more information.

## How to run it

The configuration can be either run on [CloudLab](http://cloudlab.us) (controlling
an OpenStack backend set up by a CloudLab profile) or used with a basic
[DevStack](http://docs.openstack.org/developer/devstack/) configuration.

### CloudLab

To get started on CloudLab:
* Create an experiment using the *OpenStack* profile.  Choose *Kilo* and
disable security groups.
* Wait until you get an email from CloudLab with title "OpenStack Instance Finished Setting Up".
* Login to the *ctl* node of your experiment and run:
```
ctl:~$ git clone https://github.com/open-cloud/xos.git
ctl:~$ cd xos/xos/configurations/vtn/
ctl:~/xos/xos/configurations/vtn$ make cloudlab
```

The configuration provides an Ansible script that automates the configuration
steps outlined in [the VTN README](../cord/README-VTN.md).  Run:
```
ctl:~/xos/xos/configurations/vtn$ make destroy-networks
ctl:~/xos/xos/configurations/vtn$ sudo ansible-playbook setup.yml
```


### DevStack

*NOTE: THIS CONFIGURATION IS NOT YET WORKING WITH DEVSTACK.*

The following instructions can be used to install DevStack and XOS together
on a single node.  This setup has been run successfully in a VirtualBox VM
with 2 CPUs and 4096 GB RAM.

First, if you happen to be installing DevStack on a CloudLab node, you can
configure about 1TB of unallocated disk space for DevStack as follows:
```
~$ sudo mkdir -p /opt/stack
~$ sudo /usr/testbed/bin/mkextrafs /opt/stack
```

To install DevStack and XOS:

```
~$ git clone https://github.com/open-cloud/xos.git
~$ git clone https://git.openstack.org/openstack-dev/devstack
~$ cd devstack
~/devstack$ cp ../xos/xos/configurations/common/devstack/local.conf .
~/devstack$ ./stack.sh
~/devstack$ cd ../xos/xos/configurations/devel/
~/xos/xos/configurations/devel$ make devstack
```

## Docker Helpers

Stop the containers: `make stop`

Restart the containers: `make stop; make [cloudlab|devstack]`

Delete the containers and relaunch them: `make rm; make [cloudlab|devstack]`

Build the containers from scratch using the local XOS source tree: `make containers`

View logs: `make showlogs`

See what containers are running: `make ps`

Open a shell on the XOS container: `make enter-xos`

Open a shell on the Synchronizer container: `make enter-synchronizer`
