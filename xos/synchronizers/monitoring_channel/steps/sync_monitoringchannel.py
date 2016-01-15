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
from observers.base.SyncInstanceUsingAnsible import SyncInstanceUsingAnsible
from core.models import Service, Slice
from services.ceilometer.models import MonitoringChannel
from xos.logger import Logger, logging

parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0,parentdir)

logger = Logger(level=logging.INFO)

class SyncMonitoringChannel(SyncInstanceUsingAnsible):
    provides=[MonitoringChannel]
    observes=MonitoringChannel
    requested_interval=0
    template_name = "sync_monitoringchannel.yaml"
    service_key_name = "/opt/xos/observers/monitoring_channel/monitoring_channel_private_key"

    def __init__(self, *args, **kwargs):
        super(SyncMonitoringChannel, self).__init__(*args, **kwargs)

    def fetch_pending(self, deleted):
        if (not deleted):
            objs = MonitoringChannel.get_tenant_objects().filter(Q(enacted__lt=F('updated')) | Q(enacted=None),Q(lazy_blocked=False))
        else:
            objs = MonitoringChannel.get_deleted_tenant_objects()

        return objs

    def get_extra_attributes(self, o):
        # This is a place to include extra attributes. In the case of Monitoring Channel, we need to know
        #   1) Allowed tenant ids
        #   2) Ceilometer API service endpoint URL if running externally
        #   3) Credentials to access Ceilometer API service

        instance = self.get_instance(o)

        try:
            full_setup = Config().observer_full_setup
        except:
            full_setup = True

        fields = {"unique_id": o.id,
                  "allowed_tenant_ids": o.tenant_list,
                  "auth_url":instance.controller.auth_url,
                  "admin_user":instance.controller.admin_user,
                  "admin_password":instance.controller.admin_password,
                  "admin_tenant":instance.controller.admin_tenant,
                  "full_setup": full_setup}

        return fields

    def run_playbook(self, o, fields):
        #ansible_hash = hashlib.md5(repr(sorted(fields.items()))).hexdigest()
        #quick_update = (o.last_ansible_hash == ansible_hash)

        #if quick_update:
        #    logger.info("quick_update triggered; skipping ansible recipe")
        #else:
        super(SyncMonitoringChannel, self).run_playbook(o, fields)

        #o.last_ansible_hash = ansible_hash

    def map_delete_inputs(self, o):
        fields = {"unique_id": o.id,
                  "delete": True}
        return fields
