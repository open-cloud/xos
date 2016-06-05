from django.db import models
from core.models import Service, PlCoreBase, Slice, Instance, Tenant, TenantWithContainer, Node, Image, User, Flavor, Subscriber, NetworkParameter, NetworkParameterType, AddressPool, Port
from core.models.plcorebase import StrippedCharField
import os
from django.db import models, transaction
from django.forms.models import model_to_dict
from django.db.models import Q
from operator import itemgetter, attrgetter, methodcaller
from core.models import Tag
from core.models.service import LeastLoadedNodeScheduler
import traceback
from xos.exceptions import *
from core.models import SlicePrivilege, SitePrivilege
from sets import Set
from xos.config import Config

MCORD_KIND = "RAN" # This should be changed later I did it fo demo
MCORD_USE_VTN = getattr(Config(), "networking_use_vtn", False)
VBBU_KIND = "RAN"
VSGW_KIND = "vSGW"
VPGWC_KIND = "RAN"
vbbu_net_types = ("s1u", "s1mme", "rru")
vpgwc_net_types = ("s5s8")
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
        app_label = "mcord"
        verbose_name = "MCORD Service"

# This is the class to represent the tenant. Most of the logic is given to use
# in TenantWithContainer, however there is some configuration and logic that
# we need to define for this example.
class VBBUComponent(TenantWithContainer):

    class Meta:
        # Same as a above, HelloWorldTenantComplete is represented as a
        # TenantWithContainer, but we change the python behavior.
        proxy = True
        verbose_name = "VBBU MCORD Service Component"

    # The kind of the service is used on forms to differentiate this service
    # from the other services.
    KIND = VBBU_KIND

    # Ansible requires that the sync_attributes field contain nat_ip and nat_mac
    # these will be used to determine where to SSH to for ansible.
    # Getters must be defined for every attribute specified here.
    sync_attributes = ("s1u_ip", "s1u_mac",
                       "s1mme_ip", "s1mme_mac",
                       "rru_ip", "rru_mac")
    # default_attributes is used cleanly indicate what the default values for
    # the fields are.
    default_attributes = {"display_message": "New vBBU Component", "s1u_tag": "901", "s1mme_tag": "900", "rru_tag": "999"}
    def __init__(self, *args, **kwargs):
        mcord_services = MCORDService.get_service_objects().all()
        # When the tenant is created the default service in the form is set
        # to be the first created HelloWorldServiceComplete
        if mcord_services:
            self._meta.get_field(
                "provider_service").default = mcord_services[0].id
        super(VBBUComponent, self).__init__(*args, **kwargs)

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

        super(VBBUComponent, self).save(*args, **kwargs)
        # This call needs to happen so that an instance is created for this
        # tenant is created in the slice. One instance is created per tenant.
        model_policy_mcord_servicecomponent(self.pk)

    def save_instance(self, instance):
        with transaction.atomic():
            super(VBBUComponent, self).save_instance(instance)
            if instance.isolation in ["vm"]:
                for ntype in vbbu_net_types:
                    lan_network = self.get_lan_network(instance, ntype)
                    port = self.find_or_make_port(instance,lan_network)
                    if (ntype == "s1u"):
                        port.set_parameter("s_tag", self.s1u_tag)
                        port.set_parameter("neutron_port_name", "stag-%s" % self.s1u_tag)
                        port.save()
                    elif (ntype == "s1mme"):
                        port.set_parameter("s_tag", self.s1mme_tag)
                        port.set_parameter("neutron_port_name", "stag-%s" % self.s1mme_tag)
                        port.save()
                    elif (ntype == "rru"):
                        port.set_parameter("s_tag", self.rru_tag)
                        port.set_parameter("neutron_port_name", "stag-%s" % self.rru_tag)
                        port.save()
    
    def delete(self, *args, **kwargs):
        # Delete the instance that was created for this tenant
        self.cleanup_container()
        super(VBBUComponent, self).delete(*args, **kwargs)

    def find_or_make_port(self, instance, network, **kwargs):
        port = Port.objects.filter(instance=instance, network=network)
        if port:
            port = port[0]
            print "port already exist", port[0]
        else:
            port = Port(instance=instance, network=network, **kwargs)
            print "NETWORK", network, "MAKE_PORT", port 
            port.save()
        return port

    def get_lan_network(self, instance, ntype):
        slice = self.provider_service.slices.all()[0]
        lan_networks = [x for x in slice.networks.all() if ntype in x.name]
        if not lan_networks:
            raise XOSProgrammingError("No lan_network")
        return lan_networks[0]

    def manage_container(self):
        from core.models import Instance, Flavor

        if self.deleted:
            return

        # For container or container_vm isolation, use what TenantWithCotnainer
        # provides us
        slice = self.get_slice()
        if slice.default_isolation in ["container_vm", "container"]:
            super(VBBUComponent,self).manage_container()
            return

        if not self.s1u_tag:
            raise XOSConfigurationError("S1U_TAG is missed")

        if not self.s1mme_tag:
            raise XOSConfigurationError("S1U_TAG is missed")

        if not self.rru_tag:
            raise XOSConfigurationError("S1U_TAG is missed")

        if self.instance:
            # We're good.
            return

        instance = self.make_instance()
        self.instance = instance
        super(TenantWithContainer, self).save()

    def get_slice(self):
        if not self.provider_service.slices.count():
            raise XOSConfigurationError("The service has no slices")
        slice = self.provider_service.slices.all()[0]
        return slice

    def make_instance(self):
        slice = self.provider_service.slices.all()[0]            
        flavors = Flavor.objects.filter(name=slice.default_flavor)
#        flavors = Flavor.objects.filter(name="m1.xlarge")
        if not flavors:
            raise XOSConfigurationError("No default flavor")
        default_flavor = slice.default_flavor
        slice = self.provider_service.slices.all()[0]
        if slice.default_isolation == "container_vm":
            (node, parent) = ContainerVmScheduler(slice).pick()
        else:
            (node, parent) = LeastLoadedNodeScheduler(slice).pick()
        instance = Instance(slice = slice,
                        node = node,
                        image = self.image,
                        creator = self.creator,
                        deployment = node.site_deployment.deployment,
                        flavor = flavors[0],
                        isolation = slice.default_isolation,
                        parent = parent)
        self.save_instance(instance)
        return instance

    def ip_to_mac(self, ip):
        (a, b, c, d) = ip.split('.')
        return "02:42:%02x:%02x:%02x:%02x" % (int(a), int(b), int(c), int(d))

    # Getter for the message that will appear on the webpage
    # By default it is "Hello World!"
    @property
    def display_message(self):
        return self.get_attribute(
            "display_message",
            self.default_attributes['display_message'])

    @display_message.setter
    def display_message(self, value):
        self.set_attribute("display_message", value)

    @property
    def s1u_tag(self):
        return self.get_attribute(
            "s1u_tag",
            self.default_attributes['s1u_tag'])

    @s1u_tag.setter
    def s1u_tag(self, value):
        self.set_attribute("s1u_tag", value)

    @property
    def s1mme_tag(self):
        return self.get_attribute(
            "s1mme_tag",
            self.default_attributes['s1mme_tag'])

    @s1mme_tag.setter
    def s1mme_tag(self, value):
        self.set_attribute("s1mme_tag", value)

    @property
    def rru_tag(self):
        return self.get_attribute(
            "rru_tag",
            self.default_attributes['rru_tag'])

    @rru_tag.setter
    def rru_tag(self, value):
        self.set_attribute("rru_tag", value)


    @property
    def addresses(self):
        if (not self.id) or (not self.instance):
            return {}

        addresses = {}
        for ns in self.instance.ports.all():
            if "s1u" in ns.network.name.lower():
                addresses["s1u"] = (ns.ip, ns.mac)
            elif "s1mme" in ns.network.name.lower():
                addresses["s1mme"] = (ns.ip, ns.mac)
            elif "rru" in ns.network.name.lower():
                addresses["rru"] = (ns.ip, ns.mac)
        return addresses


    @property
    def s1u_ip(self):
        return self.addresses.get("s1u", (None, None))[0]
    @property
    def s1u_mac(self):
        return self.addresses.get("s1u", (None, None))[1]
    @property
    def s1mme_ip(self):
        return self.addresses.get("s1mme", (None, None))[0]
    @property
    def s1mme_mac(self):
        return self.addresses.get("s1mme", (None, None))[1]
    @property
    def rru_ip(self):
        return self.addresses.get("rru", (None, None))[0]
    @property
    def rru_mac(self):
        return self.addresses.get("rru", (None, None))[1]


# This is the class to represent the tenant. Most of the logic is given to use
# in TenantWithContainer, however there is some configuration and logic that
# we need to define for this example.
class VPGWCComponent(TenantWithContainer):

    class Meta:
        # Same as a above, HelloWorldTenantComplete is represented as a
        # TenantWithContainer, but we change the python behavior.
        proxy = True
        verbose_name = "VPGWC MCORD Service Component"

    # The kind of the service is used on forms to differentiate this service
    # from the other services.
    KIND = VPGWC_KIND

    # Ansible requires that the sync_attributes field contain nat_ip and nat_mac
    # these will be used to determine where to SSH to for ansible.
    # Getters must be defined for every attribute specified here.
    sync_attributes = ("s5s8_pgw_ip", "s5s8_pgw_mac")

    # default_attributes is used cleanly indicate what the default values for
    # the fields are.
    default_attributes = {"display_message": "New vPGWC Component", "s5s8_pgw_tag": "300"}
    def __init__(self, *args, **kwargs):
        mcord_services = MCORDService.get_service_objects().all()
        # When the tenant is created the default service in the form is set
        # to be the first created HelloWorldServiceComplete
        if mcord_services:
            self._meta.get_field(
                "provider_service").default = mcord_services[0].id
        super(VPGWCComponent, self).__init__(*args, **kwargs)

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

        super(VPGWCComponent, self).save(*args, **kwargs)
        # This call needs to happen so that an instance is created for this
        # tenant is created in the slice. One instance is created per tenant.
        model_policy_mcord_servicecomponent(self.pk)

    def save_instance(self, instance):
        with transaction.atomic():
            super(VPGWCComponent, self).save_instance(instance)
            if instance.isolation in ["vm"]:
                for ntype in vpgwc_net_types:
                    lan_network = self.get_lan_network(instance, ntype)
                    port = self.find_or_make_port(instance,lan_network)
                    if (ntype == "s5s8"):
                        port.set_parameter("s_tag", self.s5s8_pgw_tag)
                        port.set_parameter("neutron_port_name", "stag-%s" % self.s5s8_pgw_tag)
                        port.save()
                    else:
			return True

    def delete(self, *args, **kwargs):
        # Delete the instance that was created for this tenant
        self.cleanup_container()
        super(VPGWCComponent, self).delete(*args, **kwargs)

    def find_or_make_port(self, instance, network, **kwargs):
        port = Port.objects.filter(instance=instance, network=network)
        if port:
            port = port[0]
            print "port already exist", port[0]
        else:
            port = Port(instance=instance, network=network, **kwargs)
            print "NETWORK", network, "MAKE_PORT", port 
            port.save()
        return port

    def get_lan_network(self, instance, ntype):
        slice = self.provider_service.slices.all()[0]
        lan_networks = [x for x in slice.networks.all() if ntype in x.name]
        if not lan_networks:
            raise XOSProgrammingError("No lan_network")
        return lan_networks[0]

    def manage_container(self):
        from core.models import Instance, Flavor

        if self.deleted:
            return

        # For container or container_vm isolation, use what TenantWithCotnainer
        # provides us
        slice = self.get_slice()
        if slice.default_isolation in ["container_vm", "container"]:
            super(VPGWCComponent,self).manage_container()
            return

        if not self.s5s8_pgw_tag:
            raise XOSConfigurationError("S5S8_PGW_TAG is missed")

        if self.instance:
            # We're good.
            return

        instance = self.make_instance()
        self.instance = instance
        super(TenantWithContainer, self).save()

    def get_slice(self):
        if not self.provider_service.slices.count():
            raise XOSConfigurationError("The service has no slices")
        slice = self.provider_service.slices.all()[0]
        return slice

    def make_instance(self):
        slice = self.provider_service.slices.all()[0]            
        flavors = Flavor.objects.filter(name=slice.default_flavor)
#        flavors = Flavor.objects.filter(name="m1.xlarge")
        if not flavors:
            raise XOSConfigurationError("No default flavor")
        default_flavor = slice.default_flavor
        slice = self.provider_service.slices.all()[0]
        if slice.default_isolation == "container_vm":
            (node, parent) = ContainerVmScheduler(slice).pick()
        else:
            (node, parent) = LeastLoadedNodeScheduler(slice).pick()
        instance = Instance(slice = slice,
                        node = node,
                        image = self.image,
                        creator = self.creator,
                        deployment = node.site_deployment.deployment,
                        flavor = flavors[0],
                        isolation = slice.default_isolation,
                        parent = parent)
        self.save_instance(instance)
        return instance

    def ip_to_mac(self, ip):
        (a, b, c, d) = ip.split('.')
        return "02:42:%02x:%02x:%02x:%02x" % (int(a), int(b), int(c), int(d))

    # Getter for the message that will appear on the webpage
    # By default it is "Hello World!"
    @property
    def display_message(self):
        return self.get_attribute(
            "display_message",
            self.default_attributes['display_message'])

    @display_message.setter
    def display_message(self, value):
        self.set_attribute("display_message", value)

    @property
    def s5s8_pgw_tag(self):
        return self.get_attribute(
            "s5s8_pgw_tag",
            self.default_attributes['s5s8_pgw_tag'])

    @s5s8_pgw_tag.setter
    def s5s8_pgw_tag(self, value):
        self.set_attribute("s5s8_pgw_tag", value)


    @property
    def addresses(self):
        if (not self.id) or (not self.instance):
            return {}

        addresses = {}
        for ns in self.instance.ports.all():
            if "s5s8_pgw" in ns.network.name.lower():
                addresses["s5s8_pgw"] = (ns.ip, ns.mac)
        return addresses


    @property
    def s5s8_pgw_ip(self):
        return self.addresses.get("s5s8_pgw", (None, None))[0]
    @property
    def s5s8_pgw_mac(self):
        return self.addresses.get("s5s8_pgw", (None, None))[1]

def model_policy_mcord_servicecomponent(pk):
    # This section of code is atomic to prevent race conditions
    with transaction.atomic():
        # We find all of the tenants that are waiting to update
        component = VBBUComponent.objects.select_for_update().filter(pk=pk)
        if not component:
            return
        # Since this code is atomic it is safe to always use the first tenant
        component = component[0]
        component.manage_container()


def model_policy_mcord_servicecomponent(pk):
    # This section of code is atomic to prevent race conditions
    with transaction.atomic():
        # We find all of the tenants that are waiting to update
        component = VPGWCComponent.objects.select_for_update().filter(pk=pk)
        if not component:
            return
        # Since this code is atomic it is safe to always use the first tenant
        component = component[0]
        component.manage_container()
