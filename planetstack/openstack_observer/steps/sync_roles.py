import os
import base64
from django.db.models import F, Q
from planetstack.config import Config
from observer.openstacksyncstep import OpenStackSyncStep
from core.models.role import Role
from core.models.site import SiteRole, Controller, ControllerRole
from core.models.slice import SliceRole

class SyncRoles(OpenStackSyncStep):
    provides=[Role]
    requested_interval=0

    def fetch_pending(self, deleted):
        # Deleting roles is not supported yet
        if (deleted):
            return []

        site_roles = SiteRole.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))
        slice_roles = SliceRole.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))
        controller_roles = ControllerRole.objects.filter(Q(enacted__lt=F('updated')) | Q(enacted=None))

        roles = []
        for site_role in site_roles:
            roles.append(site_role)
        for slice_role in slice_roles:
            roles.append(slice_role)
        for controller_role in controller_roles:
            roles.append(controller_role)

        return roles


    def sync_record(self, role):
        if not role.enacted:
            controllers = Controller.objects.all()
       	    for controller in controllers:
                driver = self.driver.admin_driver(controller=controller.name)
                driver.create_role(role.role)
            role.save()
    
