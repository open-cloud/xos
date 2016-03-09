import os
import sys
from django.db.models import Q, F
from services.exampleservice.models import ExampleService, ExampleTenant
from synchronizers.base.SyncInstanceUsingAnsible import SyncInstanceUsingAnsible

parentdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, parentdir)

class SyncExampleTenant(SyncInstanceUsingAnsible):

    provides = [ExampleTenant]

    observes = ExampleTenant

    requested_interval = 0

    template_name = "exampletenant_playbook.yaml"

    service_key_name = "/opt/xos/synchronizers/exampleservice/exampleservice_private_key"

    def __init__(self, *args, **kwargs):
        super(SyncExampleTenant, self).__init__(*args, **kwargs)

    def fetch_pending(self, deleted):

        if (not deleted):
            objs = ExampleTenant.get_tenant_objects().filter(
                Q(enacted__lt=F('updated')) | Q(enacted=None), Q(lazy_blocked=False))
        else:
            # If this is a deletion we get all of the deleted tenants..
            objs = ExampleTenant.get_deleted_tenant_objects()

        return objs

    def get_exampleservice(self, o):
        if not o.provider_service:
            return None

        exampleservice = ExampleService.get_service_objects().filter(id=o.provider_service.id)

        if not exampleservice:
            return None

        return exampleservice[0]

    # Gets the attributes that are used by the Ansible template but are not
    # part of the set of default attributes.
    def get_extra_attributes(self, o):
        fields = {}
        fields['tenant_message'] = o.tenant_message
        exampleservice = self.get_exampleservice(o)
        fields['service_message'] = exampleservice.service_message
        return fields

