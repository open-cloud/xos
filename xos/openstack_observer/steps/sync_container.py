import hashlib
import os
import socket
import sys
import base64
import time
from django.db.models import F, Q
from xos.config import Config
from observers.base.SyncInstanceUsingAnsible import SyncInstanceUsingAnsible
from observer.syncstep import SyncStep
from observer.ansible import run_template_ssh
from core.models import Service, Slice, Instance
from services.onos.models import ONOSService, ONOSApp
from util.logger import Logger, logging

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

    def get_ports(self, o):
        i=0
        ports = []
        for port in o.ports.all():
            if not port.mac:
                raise Exception("Port on network %s is not yet ready" % port.network.name)

            pd={}
            pd["device"] = "eth%d" % i
            pd["mac"] = port.mac
            pd["ip"] = port.ip

            if o.isolation == "container":
                # container on bare metal
                instance_port = self.get_instance_port(port)
                if not instance_port:
                    raise Exception("No instance on slice for port on network %s" % port.network.name)

                pd["snoop_instance_mac"] = instance_port.mac
                pd["snoop_instance_id"] = instance_port.instance.instance_id
                pd["src_device"] = ""
            else:
                # container in VM
                pd["snoop_instance_mac"] = ""
                pd["snoop_instance_id"] = ""
                pd["src_device"] = "eth%d" % i

            for (k,v) in port.get_parameters().items():
                pd[k] = v

            ports.append(pd)

            i = i + 1

        return ports

    def get_extra_attributes(self, o):
        fields={}
        fields["ansible_tag"] = "container-%s" % str(o.id)
        fields["container_name"] = "%s-%s" % (o.slice.name, str(o.id))
        fields["docker_image"] = o.image.name
        fields["ports"] = self.get_ports(o)
        if o.volumes:
            fields["volumes"] = [x.strip() for x in o.volumes.split(",")]
        else:
            fields["volumes"] = ""
        return fields

    def sync_fields(self, o, fields):
        self.run_playbook(o, fields)

    def sync_record(self, o):
        logger.info("sync'ing object %s" % str(o))

        fields = self.get_ansible_fields(o)

        # If 'o' defines a 'sync_attributes' list, then we'll copy those
        # attributes into the Ansible recipe's field list automatically.
        if hasattr(o, "sync_attributes"):
            for attribute_name in o.sync_attributes:
                fields[attribute_name] = getattr(o, attribute_name)

        fields.update(self.get_extra_attributes(o))

        self.sync_fields(o, fields)

        o.instance_id = fields["container_name"]
        o.instance_name = fields["container_name"]

        o.save()

    def run_playbook(self, o, fields):
        tStart = time.time()
        run_template_ssh(self.template_name, fields, path="container")
        logger.info("playbook execution time %d" % int(time.time()-tStart))

    def delete_record(self, m):
        pass
