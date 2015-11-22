from core.models import Service, TenantWithContainer
from django.db import transaction

HELLO_WORLD_KIND = "helloworldservice"

# The class to represent the service. Most of the service logic is given for us
# in the Service class but, we have some configuration that is specific for
# this example.
class HelloWorldService(Service):
    KIND = HELLO_WORLD_KIND

    class Meta:
        # When the proxy field is set to True the model is represented as
        # it's superclass in the database, but we can still change the pyhton
        # behavior. In this case HelloWorldService is a Service in the database.
        proxy = True
        # The name used to find this service, all directories are named this
        app_label = "Hello World Service"
        verbose_name = "Hello World Service"

# This is the class to represent the tenant. Most of the logic is given to use
# in TenantWithContainer, however there is some configuration and logic that
# we need to define for this example.
class HelloWorldTenant(TenantWithContainer):

    class Meta:
        # Same as a above, HelloWorldTenant is represented as a
        # TenantWithContainer, but we change the python behavior.
        proxy = True

    # The kind of the service is used on forms to differentiate this service
    # from the other services.
    KIND = HELLO_WORLD_KIND

    # Ansible requires that the sync_attributes field contain nat_ip and nat_mac
    # these will be used to determine where to SSH to for ansible.
    # Getters must be defined for every attribute specified here.
    sync_attributes = ("nat_ip", "nat_mac",)

    # default_attributes is used cleanly indicate what the default values for
    # the fields are.
    default_attributes = {'display_message': 'Hello World!'}

    def __init__(self, *args, **kwargs):
        helloworld_services = HelloWorldService.get_service_objects().all()
        # When the tenant is created the default service in the form is set
        # to be the first created HelloWorldService
        if helloworld_services:
            self._meta.get_field(
                "provider_service").default = helloworld_services[0].id
        super(HelloWorldTenant, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        super(HelloWorldTenant, self).save(*args, **kwargs)
        # This call needs to happen so that an instance is created for this
        # tenant is created in the slice. One instance is created per tenant.
        model_policy_helloworld_tenant(self.pk)

    def delete(self, *args, **kwargs):
        # Delete the instance that was created for this tenant
        self.cleanup_container()
        super(HelloWorldTenant, self).delete(*args, **kwargs)

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
        # The ports field refers to networks for the instnace.
        # This loop stores the details for the NAT network that will be
        # necessary for ansible..
        for ns in self.instance.ports.all():
            if "nat" in ns.network.name.lower():
                addresses["nat"] = (ns.ip, ns.mac)
        return addresses

    # This getter is necessary because nat_ip is a sync_attribute
    @property
    def nat_ip(self):
        return self.addresses.get("nat", (None, None))[0]

    # This getter is necessary because nat_mac is a sync_attribute
    @property
    def nat_mac(self):
        return self.addresses.get("nat", (None, None))[1]

def model_policy_helloworld_tenant(pk):
    # This section of code is atomic to prevent race conditions
    with transaction.atomic():
        # We find all of the tenants that are waiting to update
        tenant = HelloWorldTenant.objects.select_for_update().filter(pk=pk)
        if not tenant:
            return
        # Since this code is atomic it is safe to always use the first tenant
        tenant = tenant[0]
        tenant.manage_container()
