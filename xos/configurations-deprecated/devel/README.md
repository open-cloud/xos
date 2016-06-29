# XOS development environment

This configuration can be used to do basic end-to-end development of XOS.  It launches
XOS in three Docker containers (development GUI, Synchronizer, database) and configures XOS
to talk to an OpenStack backend.  *docker-compose* is used to manage the containers.

**NOTE: If your goal is to create a development environment for [CORD](http://opencord.org/), 
this configuration is not what you want.  Look at the [cord-pod](../cord-pod) configuration instead!**

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

On a server with a fresh Ubuntu 14.04 install, 
[this script](https://raw.githubusercontent.com/open-cloud/xos/master/xos/configurations/common/devstack/setup-devstack.sh)
can be used to bootstrap a single-node DevStack environment that can be used
for basic XOS development.
The script installs DevStack and checks out the XOS repository.  Run the script
and then invoke the XOS configuration for DevStack as follows:
```
~$ wget https://raw.githubusercontent.com/open-cloud/xos/master/xos/configurations/common/devstack/setup-devstack.sh
~$ bash ./setup-devstack.sh
~$ cd ../xos/xos/configurations/devel/
~/xos/xos/configurations/devel$ make devstack
```

This setup has been run successfully in a VirtualBox VM with 2 CPUs and 4096 GB RAM.
However it is recommended to use a dedicated server with more resources.


## What you get

XOS will be set up with a single Deployment and Site.  It should be in a state where
you can create slices and associate instances with them.

Note that there are some issues with the networking setup in this configuration:
VMs do not have a working DNS configuration in `/etc/resolv.conf`.  If you fix this
manually then everything should work.

## Docker Helpers

Stop the containers: `make stop`

Restart the containers: `make stop; make [cloudlab|devstack]`

Delete the containers and relaunch them: `make rm; make [cloudlab|devstack]`

Build the containers from scratch using the local XOS source tree: `make containers`

View logs: `make showlogs`

See what containers are running: `make ps`

Open a shell on the XOS container: `make enter-xos`

Open a shell on the Synchronizer container: `make enter-synchronizer`
