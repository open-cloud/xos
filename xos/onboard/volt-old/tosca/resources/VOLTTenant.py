import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate
import pdb

from core.models import User
from services.volt.models import VOLTTenant, VOLTService, CordSubscriberRoot, VOLT_KIND

from xosresource import XOSResource

class XOSVOLTTenant(XOSResource):
    provides = "tosca.nodes.VOLTTenant"
    xos_model = VOLTTenant
    copyin_props = ["service_specific_id", "s_tag", "c_tag"]
    name_field = None

    def get_xos_args(self, throw_exception=True):
        args = super(XOSVOLTTenant, self).get_xos_args()

        provider_name = self.get_requirement("tosca.relationships.MemberOfService", throw_exception=throw_exception)
        if provider_name:
            args["provider_service"] = self.get_xos_object(VOLTService, throw_exception=throw_exception, name=provider_name)

        subscriber_name = self.get_requirement("tosca.relationships.BelongsToSubscriber")
        if subscriber_name:
            args["subscriber_root"] = self.get_xos_object(CordSubscriberRoot, throw_exception=throw_exception, name=subscriber_name)

        return args

    def get_existing_objs(self):
        args = self.get_xos_args(throw_exception=False)
        provider_service = args.get("provider_service", None)
        service_specific_id = args.get("service_specific_id", None)
        if (provider_service) and (service_specific_id):
            existing_obj = self.get_xos_object(VOLTTenant, kind=VOLT_KIND, provider_service=provider_service, service_specific_id=service_specific_id, throw_exception=False)
            if existing_obj:
                return [ existing_obj ]
        return []

    def postprocess(self, obj):
        pass

    def can_delete(self, obj):
        return super(XOSVOLTTenant, self).can_delete(obj)

