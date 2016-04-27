import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate
import pdb

from core.models import User, TenantAttribute, Service
from services.onos.models import ONOSApp, ONOSService

from xosresource import XOSResource

class XOSONOSApp(XOSResource):
    provides = ["tosca.nodes.ONOSApp", "tosca.nodes.ONOSvBNGApp", "tosca.nodes.ONOSvOLTApp", "tosca.nodes.ONOSVTNApp"]
    xos_model = ONOSApp
    copyin_props = ["service_specific_id", "dependencies", "install_dependencies"]

    def get_xos_args(self, throw_exception=True):
        args = super(XOSONOSApp, self).get_xos_args()

        # provider_service is mandatory and must be the ONOS Service
        provider_name = self.get_requirement("tosca.relationships.TenantOfService", throw_exception=throw_exception)
        if provider_name:
            args["provider_service"] = self.get_xos_object(ONOSService, throw_exception=throw_exception, name=provider_name)

        # subscriber_service is optional and can be any service
        subscriber_name = self.get_requirement("tosca.relationships.UsedByService", throw_exception=False)
        if subscriber_name:
            args["subscriber_service"] = self.get_xos_object(Service, throw_exception=throw_exception, name=subscriber_name)

        return args

    def get_existing_objs(self):
        objs = ONOSApp.get_tenant_objects().all()
        objs = [x for x in objs if x.name == self.obj_name]
        return objs

    def set_tenant_attr(self, obj, prop_name, value):
        value = self.try_intrinsic_function(value)
        if value:
            attrs = TenantAttribute.objects.filter(tenant=obj, name=prop_name)
            if attrs:
                attr = attrs[0]
                if attr.value != value:
                    self.info("updating attribute %s" % prop_name)
                    attr.value = value
                    attr.save()
            else:
                self.info("adding attribute %s" % prop_name)
                ta = TenantAttribute(tenant=obj, name=prop_name, value=value)
                ta.save()

    def postprocess(self, obj):
        props = self.nodetemplate.get_properties()
        for (k,d) in props.items():
            v = d.value
            if k.startswith("config_"):
                self.set_tenant_attr(obj, k, v)
            elif k.startswith("rest_") and (k!="rest_hostname") and (k!="rest_port"):
                self.set_tenant_attr(obj, k, v)
            elif k.startswith("component_config"):
                self.set_tenant_attr(obj, k, v)
            elif k == "autogenerate":
                self.set_tenant_attr(obj, k, v)

    def can_delete(self, obj):
        return super(XOSONOSApp, self).can_delete(obj)
