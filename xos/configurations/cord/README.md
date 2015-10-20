# CORD development environment

This configuration can be used to set up a CORD development environment.
It does the following:

* Configures XOS with the CORD services: vCPE, vBNG, vOLT
* Brings up ONOS apps for controlling the dataplane: virtualbng, olt
* Sets up a basic dataplane for testing end-to-end packet flow between a subscriber client and the Internet

**NOTE:** This configuration is under **active development** and is not yet finished!  Some features are not
fully working yet.

## How to run it

The configuration is intended to be run on [CloudLab](http://cloudlab.us), on the *ctl* node set up by the OpenStack profile.
It launches an XOS container on Cloudlab that runs the XOS develserver.  The container is left running in the background.

Running `make` in this directory creates the XOS Docker container and runs the TOSCA engine with `cord.yaml` to
configure XOS with the CORD services.  In addition, a number of VMs are created:

1. *Slice mysite_onos*: runs the ONOS Docker container with `virtualbng` app loaded
1. *Slice mysite_onos*: runs the ONOS Docker container with `olt` app loaded
1. *Slice mysite_vbng*: for running OvS with the `virtualbng` app as controller
1. *Slice mysite_volt*: for running OvS with the `olt` app as controller
1. *Slice mysite_clients*: a subscriber client for end-to-end testing

After the first VM is created (for running the virtualbng app) it is necessary to configure XOS's *service_vbng* with its URL.
Log into XOS, click on *Services* tab at left, then *service_vbng* icon.  Change **Vbng url:** to point to the IP address on
`flat-lan-1-net` of the VM (will start with 10.11).

Once all the VMs are up and the ONOS apps are configured, XOS should be able to get an address mapping from the `virtualbng`
ONOS app when creating a vCPE.  To test this:

* Enter the XOS Docker container
* `$ cd /opt/xos/configurations/cord/`
* `$ make -f Makefile.inside setup_subscriber`

After a bit, a new VM should be created in slice *mysite_vcpe* running the vCPE Docker container.  To verify that it has
received an IP address mapping, look at the **Routeable subnet** field in the appropriate *Vbng tenant* object in XOS.  It should contain an IP address in the 10.254.0.0/24 subnet.
