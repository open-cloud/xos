#! /usr/bin/env python

"""
    Check the status of libvirt, openstack-nova-compute, and
    quantum-openvswitch-agent. If these services are enabled and have failed,
    then restart them.
"""

import os
import sys
import subprocess
import time

def get_systemd_status(service):
    p=subprocess.Popen(["/bin/systemctl", "is-active", service], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = p.communicate()
    out = out.strip()
    return out

libvirt_enabled = os.system("systemctl -q is-enabled libvirtd.service")==0
nova_compute_enabled = os.system("systemctl -q is-enabled openstack-nova-compute.service")==0
openvswitch_agent_enabled = os.system("systemctl -q is-enabled quantum-openvswitch-agent.service")==0

print "enabled:"
print "  libvirtd=", libvirt_enabled
print "  openstack-nova-compute=", nova_compute_enabled
print "  quantum-openvswitch-agent=", openvswitch_agent_enabled

if (not libvirt_enabled) or (not nova_compute_enabled) or (not openvswitch_agent_enabled):
    print "services are not enabled. exiting"
    sys.exit(0)

libvirt_status = get_systemd_status("libvirtd.service")
nova_compute_status = get_systemd_status("openstack-nova-compute.service")
openvswitch_agent_status = get_systemd_status("quantum-openvswitch-agent.service")

print "status:"
print "  libvirtd=", libvirt_status
print "  openstack-nova-compute=", nova_compute_status
print "  quantum-openvswitch-agent=", openvswitch_agent_status

if (libvirt_status=="failed") or (nova_compute_status=="failed") or (openvswitch_agent_status=="failed"):
    print "services have failed. doing the big restart"
    os.system("systemctl stop openstack-nova-compute.service")
    os.system("systemctl stop quantum-openvswitch-agent.service")
    os.system("systemctl stop libvirtd.service")
    time.sleep(5)
    os.system("systemctl start libvirtd.service")
    time.sleep(5)
    os.system("systemctl start quantum-openvswitch-agent.service")
    time.sleep(5)
    os.system("systemctl start openstack-nova-compute.service")
    print "done"




