# XOS development environment

This configuration can be used to do basic end-to-end development of XOS.  It launches
an XOS container, runs the XOS develserver, and configures XOS to talk to an OpenStack
backend.  

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
ctl:~$ cd xos/xos/configurations/devel/
ctl:~/xos/xos/configurations/devel$ make cloudlab
```

### DevStack

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

## What you get

XOS will be set up with a single Deployment and Site.  It should be in a state where
you can create slices and associate instances with them.

Note that there are some issues with the networking setup in this configuration:
VMs do not have a working DNS configuration in `/etc/resolv.conf`.  If you fix this
manually then everything should work.
