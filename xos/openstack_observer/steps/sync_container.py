import hashlib
import os
import socket
import sys
import base64
import time
from django.db.models import F, Q
from xos.config import Config
from observer.syncstep import SyncStep
from observer.ansible import run_template_ssh
from core.models import Service, Slice, Container
from services.onos.models import ONOSService, ONOSApp
from util.logger import Logger, logging

# hpclibrary will be in steps/..
parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

logger = Logger(level=logging.INFO)

class SyncContainer(SyncStep):
    provides=[Container]
    observes=Container
    requested_interval=0
    template_name = "sync_container.yaml"

    def __init__(self, *args, **kwargs):
        super(SyncContainer, self).__init__(*args, **kwargs)

#    def fetch_pending(self, deleted):
#        if (not deleted):
#            objs = ONOSService.get_service_objects().filter(Q(enacted__lt=F('updated')) | Q(enacted=None),Q(lazy_blocked=False))
#        else:
#            objs = ONOSService.get_deleted_service_objects()
#
#        return objs

    def get_node(self,o):
        return o.node

    def get_node_key(self, node):
        return "/opt/xos/node-key"

    def get_extra_attributes(self, o):
        fields={}
        fields["ansible_tag"] = "container-%s" % str(o.id)
        fields["baremetal_ssh"] = True
        fields["instance_name"] = "rootcontext"
        fields["container_name"] = o.name
        fields["docker_image"] = o.docker_image
        fields["username"] = "xos"
        return fields

    def sync_fields(self, o, fields):
        self.run_playbook(o, fields)

    def sync_record(self, o):
        logger.info("sync'ing object %s" % str(o))

        node = self.get_node(o)
        node_key_name = self.get_node_key(node)

        if not os.path.exists(node_key_name):
            raise Exception("Node key %s does not exist" % node_key_name)

        node_key = file(node_key_name).read()

        fields = { "hostname": node.name,
                   "private_key": node_key,
                 }

        # If 'o' defines a 'sync_attributes' list, then we'll copy those
        # attributes into the Ansible recipe's field list automatically.
        if hasattr(o, "sync_attributes"):
            for attribute_name in o.sync_attributes:
                fields[attribute_name] = getattr(o, attribute_name)

        fields.update(self.get_extra_attributes(o))

        self.sync_fields(o, fields)

        o.save()

    def run_playbook(self, o, fields):
        tStart = time.time()
        run_template_ssh(self.template_name, fields, path="container")
        logger.info("playbook execution time %d" % int(time.time()-tStart))

    def delete_record(self, m):
        pass
