import hashlib
import os
import socket
import socket
import sys
import base64
import time
import re
import json
from django.db.models import F, Q
from xos.config import Config
from synchronizers.base.syncstep import SyncStep
from synchronizers.base.ansible import run_template_ssh
from synchronizers.base.SyncInstanceUsingAnsible import SyncInstanceUsingAnsible
from core.models import Service, Slice, ControllerSlice, ControllerUser
from services.ceilometer.models import SFlowService, SFlowTenant
from xos.logger import Logger, logging

# hpclibrary will be in steps/..
parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

logger = Logger(level=logging.INFO)

class SyncSFlowTenant(SyncInstanceUsingAnsible):
    provides=[SFlowTenant]
    observes=SFlowTenant
    requested_interval=0
    template_name = "sync_sflowtenant.yaml"
    service_key_name = "/opt/xos/synchronizers/monitoring_channel/monitoring_channel_private_key"

    def __init__(self, *args, **kwargs):
        super(SyncSFlowTenant, self).__init__(*args, **kwargs)

    def fetch_pending(self, deleted):
        if (not deleted):
            objs = SFlowTenant.get_tenant_objects().filter(Q(enacted__lt=F('updated')) | Q(enacted=None),Q(lazy_blocked=False))
        else:
            objs = SFlowTenant.get_deleted_tenant_objects()

        return objs

    def get_sflow_service(self, o):
        sflows = SFlowService.get_service_objects().filter(id=o.provider_service.id)
        if not sflows:
           raise "No associated SFlow service"

        return sflows[0]

    def get_instance(self, o):
        # We assume the SFlow service owns a slice, so pick one of the instances
        # inside that slice to sync to.

        serv = self.get_sflow_service(o)

        if serv.slices.exists():
            slice = serv.slices.all()[0]
            if slice.instances.exists():
                return slice.instances.all()[0]

        return None

    def get_extra_attributes(self, o):
        instance = self.get_instance(o)

        fields={}
        fields["sflow_api_base_url"] = self.get_sflow_service(o).sflow_api_url
        fields["sflow_api_port"] = self.get_sflow_service(o).sflow_api_port
        fields["listening_endpoint"] = o.listening_endpoint
        fields["sflow_container"] = "sflowpubsub"

        return fields

    def sync_fields(self, o, fields):
        # the super causes the playbook to be run
        super(SyncSFlowTenant, self).sync_fields(o, fields)

    def run_playbook(self, o, fields):
        super(SyncSFlowTenant, self).run_playbook(o, fields)

    def delete_record(self, m):
        pass
