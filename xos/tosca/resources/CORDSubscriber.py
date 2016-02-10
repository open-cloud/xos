import os
import pdb
import sys
import tempfile
sys.path.append("/opt/tosca")
from translator.toscalib.tosca_template import ToscaTemplate
import pdb

from core.models import User, TenantRootPrivilege, TenantRootRole
from services.cord.models import CordSubscriberRoot

from xosresource import XOSResource

class XOSCORDSubscriber(XOSResource):
    provides = "tosca.nodes.CORDSubscriber"
    xos_model = CordSubscriberRoot
    copyin_props = ["service_specific_id", "firewall_enable", "url_filter_enable", "cdn_enable", "url_filter_level"]

    def postprocess(self, obj):
        rolemap = ( ("tosca.relationships.AdminPrivilege", "admin"), ("tosca.relationships.AccessPrivilege", "access"), )
        self.postprocess_privileges(TenantRootRole, TenantRootPrivilege, rolemap, obj, "tenant_root")

    def can_delete(self, obj):
        return super(XOSCORDSubscriber, self).can_delete(obj)

