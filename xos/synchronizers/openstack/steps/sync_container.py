import hashlib
import os
import socket
import sys
import base64
import time
from django.db.models import F, Q
from xos.config import Config
from synchronizers.base.SyncInstanceUsingAnsible import SyncInstanceUsingAnsible
from synchronizers.base.syncstep import SyncStep, DeferredException
from synchronizers.base.ansible import run_template_ssh
from core.models import Service, Slice, Instance
from xos.logger import Logger, logging

# hpclibrary will be in steps/..
parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

logger = Logger(level=logging.INFO)

class SyncContainer(SyncInstanceUsingAnsible):
    provides=[Instance]
    observes=Instance
    requested_interval=0
    template_name = "sync_container.yaml"

    def __init__(self, *args, **kwargs):
        super(SyncContainer, self).__init__(*args, **kwargs)

    def fetch_pending(self, deletion=False):
        objs = super(SyncContainer, self).fetch_pending(deletion)
        objs = [x for x in objs if x.isolation in ["container", "container_vm"]]
        return objs

    def get_instance_port(self, container_port):
        for p in container_port.network.links.all():
            if (p.instance) and (p.instance.isolation=="vm") and (p.instance.node == container_port.instance.node) and (p.mac):
                return p
        return None

    def get_parent_port_mac(self, instance, port):
        if not instance.parent:
            raise Exception("instance has no parent")
        for parent_port in instance.parent.ports.all():
            if parent_port.network == port.network:
                if not parent_port.mac:
                     raise DeferredException("parent port on network %s does not have mac yet" % parent_port.network.name)
                return parent_port.mac
        raise Exception("failed to find corresponding parent port for network %s" % port.network.name)

    def get_ports(self, o):
        i=0
        ports = []
        if (o.slice.network in ["host", "bridged"]):
            pass # no ports in host or bridged mode
        else:
            for port in o.ports.all():
                if (not port.ip):
                    # 'unmanaged' ports may have an ip, but no mac
                    # XXX: are there any ports that have a mac but no ip?
                    raise DeferredException("Port on network %s is not yet ready" % port.network.name)

                pd={}
                pd["mac"] = port.mac or ""
                pd["ip"] = port.ip or ""
                pd["xos_network_id"] = port.network.id

                if port.network.name == "wan_network":
                    if port.ip:
                        (a, b, c, d) = port.ip.split('.')
                        pd["mac"] = "02:42:%02x:%02x:%02x:%02x" % (int(a), int(b), int(c), int(d))


                if o.isolation == "container":
                    # container on bare metal
                    instance_port = self.get_instance_port(port)
                    if not instance_port:
                        raise DeferredException("No instance on slice for port on network %s" % port.network.name)

                    pd["snoop_instance_mac"] = instance_port.mac
                    pd["snoop_instance_id"] = instance_port.instance.instance_id
                    pd["src_device"] = ""
                    pd["bridge"] = "br-int"
                else:
                    # container in VM
                    pd["snoop_instance_mac"] = ""
                    pd["snoop_instance_id"] = ""
                    pd["parent_mac"] = self.get_parent_port_mac(o, port)
                    pd["bridge"] = ""

                for (k,v) in port.get_parameters().items():
                    pd[k] = v

                ports.append(pd)

            # for any ports that don't have a device, assign one
            used_ports = [x["device"] for x in ports if ("device" in x)]
            avail_ports = ["eth%d"%i for i in range(0,64) if ("eth%d"%i not in used_ports)]
            for port in ports:
                if not port.get("device",None):
                    port["device"] = avail_ports.pop(0)

        return ports

    def get_extra_attributes(self, o):
        fields={}
        fields["ansible_tag"] = "container-%s" % str(o.id)
        if o.image.tag:
            fields["docker_image"] = o.image.path + ":" + o.image.tag
        else:
            fields["docker_image"] = o.image.path
        fields["ports"] = self.get_ports(o)
        if o.volumes:
            fields["volumes"] = [x.strip() for x in o.volumes.split(",")]
        else:
            fields["volumes"] = ""
        fields["network_method"] = o.slice.network or "default"
        return fields

    def sync_record(self, o):
        logger.info("sync'ing object %s" % str(o),extra=o.tologdict())

        fields = self.get_ansible_fields(o)

        # If 'o' defines a 'sync_attributes' list, then we'll copy those
        # attributes into the Ansible recipe's field list automatically.
        if hasattr(o, "sync_attributes"):
            for attribute_name in o.sync_attributes:
                fields[attribute_name] = getattr(o, attribute_name)

        fields.update(self.get_extra_attributes(o))

        self.run_playbook(o, fields)

        o.instance_id = fields["container_name"]
        o.instance_name = fields["container_name"]

        o.save()

    def delete_record(self, o):
        logger.info("delete'ing object %s" % str(o),extra=o.tologdict())

        fields = self.get_ansible_fields(o)

        # If 'o' defines a 'sync_attributes' list, then we'll copy those
        # attributes into the Ansible recipe's field list automatically.
        if hasattr(o, "sync_attributes"):
            for attribute_name in o.sync_attributes:
                fields[attribute_name] = getattr(o, attribute_name)

        fields.update(self.get_extra_attributes(o))

        self.run_playbook(o, fields, "teardown_container.yaml")

    def run_playbook(self, o, fields, template_name=None):
        if not template_name:
            template_name = self.template_name
        tStart = time.time()
        run_template_ssh(template_name, fields, path="container")
        logger.info("playbook execution time %d" % int(time.time()-tStart),extra=o.tologdict())


