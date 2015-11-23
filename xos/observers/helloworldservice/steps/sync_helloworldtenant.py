import os
import sys
from django.db.models import Q, F
from helloworldservice.models import HelloWorldService, HelloWorldTenant
from observers.base.SyncInstanceUsingAnsible import SyncInstanceUsingAnsible

parentdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, parentdir)

# Class to define how we sync a tenant. Using SyncInstanceUsingAnsible we
# indicate where the find the YAML for ansible, where to find the SSH key,
# and the logic for determining what tenant needs updating, what additional
# attributes are needed, and how to delete an instance.
class SyncHelloWorldServiceTenant(SyncInstanceUsingAnsible):
    # Indicates the position in the data model, this will run when XOS needs to
    # enact a HelloWorldTenant
    provides = [HelloWorldTenant]
    # The actual model being enacted, usually the same as provides.
    observes = HelloWorldTenant
    # Number of miliseconds between interruptions of the observer
    requested_interval = 0
    # The ansible template to run
    template_name = "sync_helloworldtenant.yaml"
    # The location of the SSH private key to use when ansible connects to
    # instances.
    service_key_name = "/opt/xos/observers/helloworldservice/helloworldservice_private_key"

    def __init__(self, *args, **kwargs):
        super(SyncHelloWorldServiceTenant, self).__init__(*args, **kwargs)

    # Defines the logic for determining what HelloWorldTenants need to be
    # enacted.
    def fetch_pending(self, deleted):
        # If the update is not a deletion, then we get all of the instnaces that
        # have been updated or have not been enacted.
        if (not deleted):
            objs = HelloWorldTenant.get_tenant_objects().filter(
                Q(enacted__lt=F('updated')) | Q(enacted=None), Q(lazy_blocked=False))
        else:
            # If this is a deletion we get all of the deleted tenants..
            objs = HelloWorldTenant.get_deleted_tenant_objects()

        return objs

    # Gets the attributes that are used by the Ansible template but are not
    # part of the set of default attributes.
    def get_extra_attributes(self, o):
        return {"display_message": o.display_message}

    # Defines how to delete a HelloWorldTenant, since we don't have anyhting
    # special to cleanup or dependencies we do nothing.
    def delete_record(self, m):
        return
