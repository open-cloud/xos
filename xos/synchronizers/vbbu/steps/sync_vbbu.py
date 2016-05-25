import os
import sys
from django.db.models import Q, F
from services.mcord.models import MCORDService, VBBUComponent
from synchronizers.base.SyncInstanceUsingAnsible import SyncInstanceUsingAnsible

parentdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, parentdir)

class SyncVBBUComponent(SyncInstanceUsingAnsible):

    provides = [VBBUComponent]

    observes = VBBUComponent

    requested_interval = 0

    template_name = "sync_vbbu.yaml"

    service_key_name = "/opt/xos/configurations/mcord/mcord_private_key"

    def __init__(self, *args, **kwargs):
        super(SyncVBBUComponent, self).__init__(*args, **kwargs)

    def fetch_pending(self, deleted):

        if (not deleted):
            objs = VBBUComponent.get_tenant_objects().filter(
                Q(enacted__lt=F('updated')) | Q(enacted=None), Q(lazy_blocked=False))
        else:

            objs = VBBUComponent.get_deleted_tenant_objects()

        return objs

    def get_extra_attributes(self, o):
        return {"display_message": o.display_message, "s1u_tag": o.s1u_tag, "s1mme_tag": o.s1mme_tag, "rru_tag": o.rru_tag}
