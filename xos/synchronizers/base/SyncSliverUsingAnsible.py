import hashlib
import os
import socket
import sys
import base64
import time
from django.db.models import F, Q
from xos.config import Config
from synchronizers.base.syncstep import SyncStep
from synchronizers.base.ansible import run_template_ssh
from core.models import Service, Slice
from xos.logger import Logger, logging

logger = Logger(level=logging.INFO)

class SyncInstanceUsingAnsible(SyncStep):
    # All of the following should be defined for classes derived from this
    # base class. Examples below use VCPETenant.

    # provides=[VCPETenant]
    # observes=VCPETenant
    # requested_interval=0
    # template_name = "sync_vcpetenant.yaml"
    # service_key_name = "/opt/xos/observers/vcpe/vcpe_private_key"

    def __init__(self, **args):
        SyncStep.__init__(self, **args)

    def defer_sync(self, o, reason):
        logger.info("defer object %s due to %s" % (str(o), reason))
        raise Exception("defer object %s due to %s" % (str(o), reason))

    def get_extra_attributes(self, o):
        # This is a place to include extra attributes that aren't part of the
        # object itself.

        return {}

    def get_instance(self, o):
        # We need to know what instance is associated with the object. Let's
        # assume 'o' has a field called 'instance'. If the field is called
        # something else, or if custom logic is needed, then override this
        # method.

        return o.instance

    def run_playbook(self, o, fields):
        tStart = time.time()
        run_template_ssh(self.template_name, fields)
        logger.info("playbook execution time %d" % int(time.time()-tStart))

    def pre_sync_hook(self, o, fields):
        pass

    def post_sync_hook(self, o, fields):
        pass

    def sync_fields(self, o, fields):
        self.run_playbook(o, fields)

    def sync_record(self, o):
        logger.info("sync'ing object %s" % str(o))

        instance = self.get_instance(o)
        if not instance:
            self.defer_sync(o, "waiting on instance")
            return

        if not os.path.exists(self.service_key_name):
            raise Exception("Service key %s does not exist" % self.service_key_name)

        service_key = file(self.service_key_name).read()

        fields = { "instance_name": instance.name,
                   "hostname": instance.node.name,
                   "instance_id": instance.instance_id,
                   "private_key": service_key,
                   "ansible_tag": "vcpe_tenant_" + str(o.id)
                 }

        # If 'o' defines a 'sync_attributes' list, then we'll copy those
        # attributes into the Ansible recipe's field list automatically.
        if hasattr(o, "sync_attributes"):
            for attribute_name in o.sync_attributes:
                fields[attribute_name] = getattr(o, attribute_name)

        fields.update(self.get_extra_attributes(o))

        self.sync_fields(o, fields)

        o.save()

    def delete_record(self, m):
        pass

