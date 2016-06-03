import os
import base64
from collections import defaultdict
from django.db.models import F, Q
from xos.config import Config
from synchronizers.base.openstacksyncstep import OpenStackSyncStep
from synchronizers.base.syncstep import *
from core.models import Controller
from core.models import Image, ControllerImages
from xos.logger import observer_logger as logger
from synchronizers.base.ansible import *
from services.cord.models import VSGTenant
from services.onos.models import ONOSService
from services.fabric.models import FabricService
import json

class SyncVSGTenant(SyncStep):
    provides=[VSGTenant]
    observes = VSGTenant
    requested_interval=30
    playbook='sync_vsgtenant.yaml'

    def get_fabric_onos_service(self):
        fos = None
        fs = FabricService.get_service_objects().all()[0]
        if fs.subscribed_tenants.exists():
            app = fs.subscribed_tenants.all()[0]
            if app.provider_service:
                ps = app.provider_service
                fos = ONOSService(id=ps.id)
        return fos

    def get_node_tag(self, node, tagname):
        tags = Tag.select_by_content_object(node).filter(name=tagname)
        return tags[0].value

    def fetch_pending(self, deleted):
        if (not deleted):
            objs = VSGTenant.get_tenant_objects().filter(Q(lazy_blocked=False))
        else:
            objs = VSGTenant.get_deleted_tenant_objects()

        return objs

    def map_sync_inputs(self, vsgtenant):

        wan_ip = vsgtenant.wan_container_ip
        wan_mac = vsgtenant.wan_container_mac

        fos = self.get_fabric_onos_service()

        # Look up location - it's tagged on the nodes
        node = vsgtenant.instance.node
        location = self.get_node_tag(node, "location")

        # Is it a POST or DELETE?

        # Create JSON
        data = {
            "%s/-1"%wan_mac : {
                "basic" : {
                    "ips" : [ wan_ip ],
                    "location" : location
                }
            }
        }

        rest_json = json.dumps(data, indent=4)

        logger.error("object is %s" % fos.name)
        logger.error("rest_hostname is %s" % fos.rest_hostname)
        logger.error("rest_port is %s" % fos.rest_port)

        fields = {
            'rest_hostname': fos.rest_hostname,
            'rest_port': fos.rest_port,
            'rest_json': rest_json,
            'rest_endpoint': "onos/v1/network/configuration/hosts",
            'ansible_tag': '%s'%(str(vsgtenant)), # name of ansible playbook
        }
        return fields

    def map_sync_outputs(self, controller_image, res):
        pass
