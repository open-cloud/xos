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
from services.vrouter.models import VRouterTenant
from services.onos.models import ONOSService
from services.fabric.models import FabricService
import json

class SyncVRouterTenant(SyncStep):
    provides=[VRouterTenant]
    observes = VRouterTenant
    requested_interval=30
    playbook='sync_host.yaml'

    def get_fabric_onos_service(self):
        fos = None
        fs = FabricService.get_service_objects().all()[0]
        if fs.subscribed_tenants.exists():
            app = fs.subscribed_tenants.all()[0]
            if app.provider_service:
                ps = app.provider_service
                fos = ONOSService.get_service_objects().filter(id=ps.id)[0]
        return fos

    def get_node_tag(self, node, tagname):
        tags = Tag.select_by_content_object(node).filter(name=tagname)
        return tags[0].value

    def fetch_pending(self, deleted):
        fs = FabricService.get_service_objects().all()[0]
        if not fs.autoconfig:
            return None

        if (not deleted):
            objs = VRouterTenant.get_tenant_objects().filter(Q(lazy_blocked=False))
        else:
            objs = VRouterTenant.get_deleted_tenant_objects()

        return objs

    def map_sync_inputs(self, vroutertenant):

        fos = self.get_fabric_onos_service()

        name = None
        instance = None
        # VRouterTenant setup is kind of hacky right now, we'll
        # need to revisit.  The idea is:
        # * Look up the instance corresponding to the address
        # * Look up the node running the instance
        # * Get the "location" tag, push to the fabric
        #
        # Do we have a vCPE subscriber_tenant?
        if (vroutertenant.subscriber_tenant):
            sub = vroutertenant.subscriber_tenant
            if (sub.kind == 'vCPE'):
                instance_id = sub.get_attribute("instance_id")
                if instance_id:
                    instance = Instance.objects.filter(id=instance_id)[0]
                    name = str(sub)
        else:
            # Maybe the VRouterTenant is for an instance
            instance_id = vroutertenant.get_attribute("tenant_for_instance_id")
            if instance_id: 
                instance = Instance.objects.filter(id=instance_id)[0]
                name = str(instance)

        node = instance.node
        location = self.get_node_tag(node, "location")

        # Is it a POST or DELETE?

        # Create JSON
        data = {
            "%s/-1"%vroutertenant.public_mac : {
                "basic" : {
                    "ips" : [ vroutertenant.public_ip ],
                    "location" : location
                }
            }
        }

        rest_json = json.dumps(data, indent=4)

        fields = {
            'rest_hostname': fos.rest_hostname,
            'rest_port': fos.rest_port,
            'rest_json': rest_json,
            'rest_endpoint': "onos/v1/network/configuration/hosts",
            'ansible_tag': '%s'%name, # name of ansible playbook
        }
        return fields

    def map_sync_outputs(self, controller_image, res):
        pass
