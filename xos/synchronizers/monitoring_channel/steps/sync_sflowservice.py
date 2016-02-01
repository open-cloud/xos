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
from synchronizers.base.SyncInstanceUsingAnsible import SyncInstanceUsingAnsible
from core.models import Service, Slice
from services.ceilometer.models import SFlowService
from xos.logger import Logger, logging

# hpclibrary will be in steps/..
parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

logger = Logger(level=logging.INFO)

class SyncSFlowService(SyncInstanceUsingAnsible):
    provides=[SFlowService]
    observes=SFlowService
    requested_interval=0
    template_name = "sync_sflowservice.yaml"
    service_key_name = "/opt/xos/synchronizers/monitoring_channel/monitoring_channel_private_key"

    def __init__(self, *args, **kwargs):
        super(SyncSFlowService, self).__init__(*args, **kwargs)

    def fetch_pending(self, deleted):
        if (not deleted):
            objs = SFlowService.get_service_objects().filter(Q(enacted__lt=F('updated')) | Q(enacted=None),Q(lazy_blocked=False))
        else:
            objs = SFlowService.get_deleted_service_objects()

        return objs

    def get_instance(self, o):
        # We assume the ONOS service owns a slice, so pick one of the instances
        # inside that slice to sync to.

        serv = o

        if serv.slices.exists():
            slice = serv.slices.all()[0]
            if slice.instances.exists():
                return slice.instances.all()[0]

        return None

    def get_extra_attributes(self, o):
        fields={}
        fields["instance_hostname"] = self.get_instance(o).instance_name.replace("_","-")
        fields["sflow_port"] = o.sflow_port
        fields["sflow_api_port"] = o.sflow_api_port
        fields["nat_ip"] = self.get_instance(o).get_ssh_ip()
        fields["sflow_container"] = "sflowpubsub"
        return fields

    def sync_fields(self, o, fields):
        # the super causes the playbook to be run
        super(SyncSFlowService, self).sync_fields(o, fields)

    def run_playbook(self, o, fields):
        instance = self.get_instance(o)
        if (instance.isolation=="container"):
            # If the instance is already a container, then we don't need to
            # install ONOS.
            return
        super(SyncSFlowService, self).run_playbook(o, fields)

    def delete_record(self, m):
        pass
