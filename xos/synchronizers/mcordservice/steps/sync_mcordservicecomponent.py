import os
import sys
from django.db.models import Q, F
from services.mcordservice.models import MCORDService, MCORDServiceComponent
from synchronizers.base.SyncInstanceUsingAnsible import SyncInstanceUsingAnsible

parentdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, parentdir)

class SyncMCORDServiceComponent(SyncInstanceUsingAnsible):

    provides = [MCORDServiceComponent]

    observes = MCORDServiceComponent

    requested_interval = 0

    template_name = "sync_mcordservicecomponent.yaml"

    service_key_name = "/opt/xos/synchronizers/mcordservice/mcordservice_private_key"

    def __init__(self, *args, **kwargs):
        super(SyncMCORDServiceComponent, self).__init__(*args, **kwargs)

    def fetch_pending(self, deleted):

        if (not deleted):
            objs = MCORDServiceComponent.get_tenant_objects().filter(
                Q(enacted__lt=F('updated')) | Q(enacted=None), Q(lazy_blocked=False))
        else:

            objs = MCORDServiceComponent.get_deleted_tenant_objects()

        return objs

    def get_extra_attributes(self, o):
        return {"display_message": o.display_message}
