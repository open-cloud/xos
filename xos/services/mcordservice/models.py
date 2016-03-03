from django.db import models
from core.models import Service, PlCoreBase, Slice, Instance, Tenant, TenantWithContainer, Node, Image, User, Flavor, Subscriber
from core.models.plcorebase import StrippedCharField
import os
from django.db import models, transaction
from django.forms.models import model_to_dict
from django.db.models import Q
from operator import itemgetter, attrgetter, methodcaller
import traceback
from xos.exceptions import *
from core.models import SlicePrivilege, SitePrivilege
from sets import Set

MCORD_KIND = "mcordservice"

# The class to represent the service. Most of the service logic is given for us
# in the Service class but, we have some configuration that is specific for
# this example.
class MCORDService(Service):
    KIND = MCORD_KIND

    class Meta:
        # When the proxy field is set to True the model is represented as
        # it's superclass in the database, but we can still change the python
        # behavior. In this case HelloWorldServiceComplete is a Service in the
        # database.
        proxy = True
        # The name used to find this service, all directories are named this
        app_label = "mcordservice"
        verbose_name = "MCORD Service"

# This is the class to represent the tenant. Most of the logic is given to use
# in TenantWithContainer, however there is some configuration and logic that
# we need to define for this example.
class MCORDServiceComponent(TenantWithContainer):

    class Meta:
        # Same as a above, HelloWorldTenantComplete is represented as a
        # TenantWithContainer, but we change the python behavior.
        proxy = True
        verbose_name = "MCORD Service Component"

    # The kind of the service is used on forms to differentiate this service
    # from the other services.
    KIND = MCORD_KIND

    # Ansible requires that the sync_attributes field contain nat_ip and nat_mac
    # these will be used to determine where to SSH to for ansible.
    # Getters must be defined for every attribute specified here.
    sync_attributes = ("private_ip", "private_mac",
                       "mcord_ip", "mcord_mac",
                       "nat_ip", "nat_mac",)

    # default_attributes is used cleanly indicate what the default values for
    # the fields are.
    default_attributes = {'display_message': 'Hello MCORD!'}

    def __init__(self, *args, **kwargs):
        mcord_services = MCORDService.get_service_objects().all()
        # When the tenant is created the default service in the form is set
        # to be the first created HelloWorldServiceComplete
        if mcord_services:
            self._meta.get_field(
                "provider_service").default = mcord_services[0].id
        super(MCORDServiceComponent, self).__init__(*args, **kwargs)

    def can_update(self, user):
        #Allow creation of this model instances for non-admin users also
        return True

    def save(self, *args, **kwargs):
        if not self.creator:
            if not getattr(self, "caller", None):
                # caller must be set when creating a monitoring channel since it creates a slice
                raise XOSProgrammingError("ServiceComponents's self.caller was not set")
            self.creator = self.caller
            if not self.creator:
                raise XOSProgrammingError("ServiceComponents's self.creator was not set")

        super(MCORDServiceComponent, self).save(*args, **kwargs)
        # This call needs to happen so that an instance is created for this
        # tenant is created in the slice. One instance is created per tenant.
        model_policy_mcord_servicecomponent(self.pk)

    def delete(self, *args, **kwargs):
        # Delete the instance that was created for this tenant
        self.cleanup_container()
        super(MCORDServiceComponent, self).delete(*args, **kwargs)

    # Getter for the message that will appear on the webpage
    # By default it is "Hello World!"
    @property
    def display_message(self):
        return self.get_attribute(
            "display_message",
            self.default_attributes['display_message'])

    # Setter for the message that will appear on the webpage
    @display_message.setter
    def display_message(self, value):
        self.set_attribute("display_message", value)

    @property
    def addresses(self):
        if (not self.id) or (not self.instance):
            return {}

        addresses = {}
        for ns in self.instance.ports.all():
            if "private" in ns.network.name.lower():
                addresses["private"] = (ns.ip, ns.mac)
            elif "nat" in ns.network.name.lower():
                addresses["nat"] = (ns.ip, ns.mac)
            elif "mcord_service_internal_net" in ns.network.labels.lower():
                addresses["mcordservice"] = (ns.ip, ns.mac)
        return addresses

    # This getter is necessary because nat_ip is a sync_attribute
    @property
    def nat_ip(self):
        return self.addresses.get("nat", (None, None))[0]

    # This getter is necessary because nat_mac is a sync_attribute
    @property
    def nat_mac(self):
        return self.addresses.get("nat", (None, None))[1]

    @property
    def private_ip(self):
        return self.addresses.get("nat", (None, None))[0]

    @property
    def private_mac(self):
        return self.addresses.get("nat", (None, None))[1]


    @property
    def mcord_ip(self):
        return self.addresses.get("nat", (None, None))[0]

    @property
    def mcord_mac(self):
        return self.addresses.get("nat", (None, None))[1]



def model_policy_mcord_servicecomponent(pk):
    # This section of code is atomic to prevent race conditions
    with transaction.atomic():
        # We find all of the tenants that are waiting to update
        component = MCORDServiceComponent.objects.select_for_update().filter(pk=pk)
        if not component:
            return
        # Since this code is atomic it is safe to always use the first tenant
        component = component[0]
        component.manage_container()
