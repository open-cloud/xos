from django.db import models
from core.models import Service, PlCoreBase, Slice, Instance, Tenant, TenantWithContainer, Node, Image, User, Flavor, Subscriber, NetworkParameter, NetworkParameterType, Port, AddressPool
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
from xos.config import Config

class ConfigurationError(Exception):
    pass

VOLT_KIND = "vOLT"
VCPE_KIND = "vCPE"
VBNG_KIND = "vBNG"
CORD_SUBSCRIBER_KIND = "CordSubscriberRoot"

CORD_USE_VTN = getattr(Config(), "networking_use_vtn", False)

# -------------------------------------------
# CordSubscriberRoot
# -------------------------------------------

class CordSubscriberRoot(Subscriber):
    class Meta:
        proxy = True

    KIND = CORD_SUBSCRIBER_KIND

    status_choices = (("enabled", "Enabled"),
                      ("suspended", "Suspended"),
                      ("delinquent", "Delinquent"),
                      ("copyrightviolation", "Copyright Violation"))

    # 'simple_attributes' will be expanded into properties and setters that
    # store the attribute using self.set_attribute / self.get_attribute.

    simple_attributes = ( ("firewall_enable", False),
                          ("firewall_rules", "accept all anywhere anywhere"),
                          ("url_filter_enable", False),
                          ("url_filter_rules", "allow all"),
                          ("url_filter_level", "PG"),
                          ("cdn_enable", False),
                          ("users", []),
                          ("is_demo_user", False),

                          ("uplink_speed", 1000000000),  # 1 gigabit, a reasonable default?
                          ("downlink_speed", 1000000000),
                          ("enable_uverse", True) )

    default_attributes = {"status": "enabled"}

    sync_attributes = ("firewall_enable",
                       "firewall_rules",
                       "url_filter_enable",
                       "url_filter_rules",
                       "cdn_enable",
                       "uplink_speed",
                       "downlink_speed",
                       "enable_uverse",
                       "status")

    def __init__(self, *args, **kwargs):
        super(CordSubscriberRoot, self).__init__(*args, **kwargs)
        self.cached_volt = None
        self._initial_url_filter_enable = self.url_filter_enable

    @property
    def volt(self):
        volt = self.get_newest_subscribed_tenant(VOLTTenant)
        if not volt:
            return None

        # always return the same object when possible
        if (self.cached_volt) and (self.cached_volt.id == volt.id):
            return self.cached_volt

        #volt.caller = self.creator
        self.cached_volt = volt
        return volt

    @property
    def status(self):
        return self.get_attribute("status", self.default_attributes["status"])

    @status.setter
    def status(self, value):
        if not value in [x[0] for x in self.status_choices]:
            raise Exception("invalid status %s" % value)
        self.set_attribute("status", value)

    def find_user(self, uid):
        uid = int(uid)
        for user in self.users:
            if user["id"] == uid:
                return user
        return None

    def update_user(self, uid, **kwargs):
        # kwargs may be "level" or "mac"
        #    Setting one of these to None will cause None to be stored in the db
        uid = int(uid)
        users = self.users
        for user in users:
            if user["id"] == uid:
                for arg in kwargs.keys():
                    user[arg] = kwargs[arg]
                    self.users = users
                return user
        raise ValueError("User %d not found" % uid)

    def create_user(self, **kwargs):
        if "name" not in kwargs:
            raise XOSMissingField("The name field is required")

        for user in self.users:
            if kwargs["name"] == user["name"]:
                raise XOSDuplicateKey("User %s already exists" % kwargs["name"])

        uids = [x["id"] for x in self.users]
        if uids:
            uid = max(uids)+1
        else:
            uid = 0
        newuser = kwargs.copy()
        newuser["id"] = uid

        users = self.users
        users.append(newuser)
        self.users = users

        return newuser

    def delete_user(self, uid):
        uid = int(uid)
        users = self.users
        for user in users:
            if user["id"]==uid:
                users.remove(user)
                self.users = users
                return

        raise ValueError("Users %d not found" % uid)

    @property
    def services(self):
        return {"cdn": self.cdn_enable,
                "url_filter": self.url_filter_enable,
                "firewall": self.firewall_enable}

    @services.setter
    def services(self, value):
        pass

    def save(self, *args, **kwargs):
        if (not hasattr(self, 'caller') or not self.caller.is_admin):
            if (self.has_field_changed("service_specific_id")):
                raise XOSPermissionDenied("You do not have permission to change service_specific_id")
        super(CordSubscriberRoot, self).save(*args, **kwargs)
        if (self.volt) and (self.volt.vcpe): # and (self._initial_url_filter_enabled != self.url_filter_enable):
            # 1) trigger manage_bbs_account to run
            # 2) trigger vcpe observer to wake up
            self.volt.vcpe.save()

CordSubscriberRoot.setup_simple_attributes()

# -------------------------------------------
# VOLT
# -------------------------------------------

class VOLTService(Service):
    KIND = VOLT_KIND

    class Meta:
        app_label = "cord"
        verbose_name = "vOLT Service"
        proxy = True

class VOLTTenant(Tenant):
    class Meta:
        proxy = True

    KIND = VOLT_KIND

    default_attributes = {"vlan_id": None, "s_tag": None, "c_tag": None}
    def __init__(self, *args, **kwargs):
        volt_services = VOLTService.get_service_objects().all()
        if volt_services:
            self._meta.get_field("provider_service").default = volt_services[0].id
        super(VOLTTenant, self).__init__(*args, **kwargs)
        self.cached_vcpe = None

    @property
    def s_tag(self):
        return self.get_attribute("s_tag", self.default_attributes["s_tag"])

    @s_tag.setter
    def s_tag(self, value):
        self.set_attribute("s_tag", value)

    @property
    def c_tag(self):
        return self.get_attribute("c_tag", self.default_attributes["c_tag"])

    @c_tag.setter
    def c_tag(self, value):
        self.set_attribute("c_tag", value)

    # for now, vlan_id is a synonym for c_tag

    @property
    def vlan_id(self):
        return self.c_tag

    @vlan_id.setter
    def vlan_id(self, value):
        self.c_tag = value

    @property
    def vcpe(self):
        vcpe = self.get_newest_subscribed_tenant(VSGTenant)
        if not vcpe:
            return None

        # always return the same object when possible
        if (self.cached_vcpe) and (self.cached_vcpe.id == vcpe.id):
            return self.cached_vcpe

        vcpe.caller = self.creator
        self.cached_vcpe = vcpe
        return vcpe

    @vcpe.setter
    def vcpe(self, value):
        raise XOSConfigurationError("vOLT.vCPE cannot be set this way -- create a new vCPE object and set its subscriber_tenant instead")

    @property
    def subscriber(self):
        if not self.subscriber_root:
            return None
        subs = CordSubscriberRoot.objects.filter(id=self.subscriber_root.id)
        if not subs:
            return None
        return subs[0]

    @property
    def creator(self):
        if getattr(self, "cached_creator", None):
            return self.cached_creator
        creator_id=self.get_attribute("creator_id")
        if not creator_id:
            return None
        users=User.objects.filter(id=creator_id)
        if not users:
            return None
        user=users[0]
        self.cached_creator = users[0]
        return user

    @creator.setter
    def creator(self, value):
        if value:
            value = value.id
        if (value != self.get_attribute("creator_id", None)):
            self.cached_creator=None
        self.set_attribute("creator_id", value)

    def manage_vcpe(self):
        # Each VOLT object owns exactly one VCPE object

        if self.deleted:
            return

        if self.vcpe is None:
            vsgServices = VSGService.get_service_objects().all()
            if not vsgServices:
                raise XOSConfigurationError("No VSG Services available")

            vcpe = VSGTenant(provider_service = vsgServices[0],
                              subscriber_tenant = self)
            vcpe.caller = self.creator
            vcpe.save()

    def manage_subscriber(self):
        if (self.subscriber_root is None):
            # The vOLT is not connected to a Subscriber, so either find an
            # existing subscriber with the same SSID, or autogenerate a new
            # subscriber.
            #
            # TODO: This probably goes away when we rethink the ONOS-to-XOS
            # vOLT API.

            subs = CordSubscriberRoot.get_tenant_objects().filter(service_specific_id = self.service_specific_id)
            if subs:
                sub = subs[0]
            else:
                sub = CordSubscriberRoot(service_specific_id = self.service_specific_id,
                                         name = "autogenerated-for-vOLT-%s" % self.id)
                sub.save()
            self.subscriber_root = sub
            self.save()

    def cleanup_vcpe(self):
        if self.vcpe:
            # print "XXX cleanup vcpe", self.vcpe
            self.vcpe.delete()

    def cleanup_orphans(self):
        # ensure vOLT only has one vCPE
        cur_vcpe = self.vcpe
        for vcpe in list(self.get_subscribed_tenants(VSGTenant)):
            if (not cur_vcpe) or (vcpe.id != cur_vcpe.id):
                # print "XXX clean up orphaned vcpe", vcpe
                vcpe.delete()

    def save(self, *args, **kwargs):
        self.validate_unique_service_specific_id()

        if (self.subscriber_root is not None):
            subs = self.subscriber_root.get_subscribed_tenants(VOLTTenant)
            if (subs) and (self not in subs):
                raise XOSDuplicateKey("Subscriber should only be linked to one vOLT")

        if not self.creator:
            if not getattr(self, "caller", None):
                # caller must be set when creating a vCPE since it creates a slice
                raise XOSProgrammingError("VOLTTenant's self.caller was not set")
            self.creator = self.caller
            if not self.creator:
                raise XOSProgrammingError("VOLTTenant's self.creator was not set")

        super(VOLTTenant, self).save(*args, **kwargs)
        model_policy_volt(self.pk)
        #self.manage_vcpe()
        #self.manage_subscriber()
        #self.cleanup_orphans()

    def delete(self, *args, **kwargs):
        self.cleanup_vcpe()
        super(VOLTTenant, self).delete(*args, **kwargs)

def model_policy_volt(pk):
    # TODO: this should be made in to a real model_policy
    with transaction.atomic():
        volt = VOLTTenant.objects.select_for_update().filter(pk=pk)
        if not volt:
            return
        volt = volt[0]
        volt.manage_vcpe()
        volt.manage_subscriber()
        volt.cleanup_orphans()

# -------------------------------------------
# VCPE
# -------------------------------------------

class VSGService(Service):
    KIND = VCPE_KIND

    URL_FILTER_KIND_CHOICES = ( (None, "None"), ("safebrowsing", "Safe Browsing"), ("answerx", "AnswerX") )

    simple_attributes = ( ("bbs_api_hostname", None),
                          ("bbs_api_port", None),
                          ("bbs_server", None),
                          ("backend_network_label", "hpc_client"),
                          ("wan_container_gateway_ip", ""),
                          ("wan_container_gateway_mac", ""),
                          ("wan_container_netbits", "24"),
                          ("dns_servers", "8.8.8.8"),
                          ("url_filter_kind", None),
                          ("node_label", None) )

    def __init__(self, *args, **kwargs):
        super(VSGService, self).__init__(*args, **kwargs)

    class Meta:
        app_label = "cord"
        verbose_name = "vSG Service"
        proxy = True

    def allocate_bbs_account(self):
        vcpes = VSGTenant.get_tenant_objects().all()
        bbs_accounts = [vcpe.bbs_account for vcpe in vcpes]

        # There's a bit of a race here; some other user could be trying to
        # allocate a bbs_account at the same time we are.

        for i in range(2,21):
             account_name = "bbs%02d@onlab.us" % i
             if (account_name not in bbs_accounts):
                 return account_name

        raise XOSConfigurationError("We've run out of available broadbandshield accounts. Delete some vcpe and try again.")

    @property
    def bbs_slice(self):
        bbs_slice_id=self.get_attribute("bbs_slice_id")
        if not bbs_slice_id:
            return None
        bbs_slices=Slice.objects.filter(id=bbs_slice_id)
        if not bbs_slices:
            return None
        return bbs_slices[0]

    @bbs_slice.setter
    def bbs_slice(self, value):
        if value:
            value = value.id
        self.set_attribute("bbs_slice_id", value)

VSGService.setup_simple_attributes()

#class STagBlock(PlCoreBase):
#    instance = models.ForeignKey(Instance, related_name="s_tags")
#    s_tag = models.CharField(null=false, blank=false, unique=true, max_length=10)
#    #c_tags = models.TextField(null=true, blank=true)
#
#    def __unicode__(self): return u'%s' % (self.s_tag)

class VSGTenant(TenantWithContainer):
    class Meta:
        proxy = True

    KIND = VCPE_KIND

    sync_attributes = ("nat_ip", "nat_mac",
                       "lan_ip", "lan_mac",
                       "wan_ip", "wan_mac",
                       "wan_container_ip", "wan_container_mac",
                       "private_ip", "private_mac",
                       "hpc_client_ip", "hpc_client_mac")

    default_attributes = {"instance_id": None,
                          "container_id": None,
                          "users": [],
                          "bbs_account": None,
                          "last_ansible_hash": None,
                          "wan_container_ip": None}

    def __init__(self, *args, **kwargs):
        super(VSGTenant, self).__init__(*args, **kwargs)
        self.cached_vbng=None

    @property
    def vbng(self):
        vbng = self.get_newest_subscribed_tenant(VBNGTenant)
        if not vbng:
            return None

        # always return the same object when possible
        if (self.cached_vbng) and (self.cached_vbng.id == vbng.id):
            return self.cached_vbng

        vbng.caller = self.creator
        self.cached_vbng = vbng
        return vbng

    @vbng.setter
    def vbng(self, value):
        raise XOSConfigurationError("vCPE.vBNG cannot be set this way -- create a new vBNG object and set it's subscriber_tenant instead")

    @property
    def volt(self):
        if not self.subscriber_tenant:
            return None
        volts = VOLTTenant.objects.filter(id=self.subscriber_tenant.id)
        if not volts:
            return None
        return volts[0]

    @property
    def bbs_account(self):
        return self.get_attribute("bbs_account", self.default_attributes["bbs_account"])

    @bbs_account.setter
    def bbs_account(self, value):
        return self.set_attribute("bbs_account", value)

    @property
    def last_ansible_hash(self):
        return self.get_attribute("last_ansible_hash", self.default_attributes["last_ansible_hash"])

    @last_ansible_hash.setter
    def last_ansible_hash(self, value):
        return self.set_attribute("last_ansible_hash", value)

    @property
    def ssh_command(self):
        if self.instance:
            return self.instance.get_ssh_command()
        else:
            return "no-instance"

    @ssh_command.setter
    def ssh_command(self, value):
        pass

    @property
    def addresses(self):
        if self.instance:
            ports = self.instance.ports.all()
        elif self.container:
            ports = self.container.ports.all()
        else:
            return {}

        addresses = {}
        for ns in ports:
            if "lan" in ns.network.name.lower():
                addresses["lan"] = (ns.ip, ns.mac)
            elif "wan" in ns.network.name.lower():
                addresses["wan"] = (ns.ip, ns.mac)
            elif "private" in ns.network.name.lower():
                addresses["private"] = (ns.ip, ns.mac)
            elif "nat" in ns.network.name.lower():
                addresses["nat"] = (ns.ip, ns.mac)
            elif "hpc_client" in ns.network.name.lower():
                addresses["hpc_client"] = (ns.ip, ns.mac)
        return addresses

    # ------------------------------------------------------------------------
    # The following IP addresses all come from the VM
    # Note: They might not be useful for the VTN-vSG

    @property
    def nat_ip(self):
        return self.addresses.get("nat", (None,None) )[0]

    @property
    def nat_mac(self):
        return self.addresses.get("nat", (None,None) )[1]

    @property
    def lan_ip(self):
        return self.addresses.get("lan", (None, None) )[0]

    @property
    def lan_mac(self):
        return self.addresses.get("lan", (None, None) )[1]

    @property
    def wan_ip(self):
        return self.addresses.get("wan", (None, None) )[0]

    @property
    def wan_mac(self):
        return self.addresses.get("wan", (None, None) )[1]

    # end of VM IP address stubs
    # ------------------------------------------------------------------------

    @property
    def wan_container_ip(self):
        if CORD_USE_VTN:
            # When using VTN, wan_container_ip is stored and maintained inside
            # of the vSG object.
            return self.get_attribute("wan_container_ip", self.default_attributes["wan_container_ip"])
        else:
            # When not using VTN, wan_container_ip is the same as wan_ip.
            # XXX Is this broken for multiple-containers-per-VM?
            return self.wan_ip

    @wan_container_ip.setter
    def wan_container_ip(self, value):
        if CORD_USE_VTN:
            self.set_attribute("wan_container_ip", value)
        else:
            raise Exception("wan_container_ip.setter called on non-VTN CORD")

    def ip_to_mac(self, ip):
        (a, b, c, d) = ip.split('.')
        return "02:42:%02x:%02x:%02x:%02x" % (int(a), int(b), int(c), int(d))

    # Generate the MAC for the container interface connected to WAN
    @property
    def wan_container_mac(self):
        if not self.wan_container_ip:
            return None
        return self.ip_to_mac(self.wan_container_ip)

    @property
    def private_ip(self):
        return self.addresses.get("private", (None, None) )[0]

    @property
    def private_mac(self):
        return self.addresses.get("private", (None, None) )[1]

    @property
    def hpc_client_ip(self):
        return self.addresses.get("hpc_client", (None, None) )[0]

    @property
    def hpc_client_mac(self):
        return self.addresses.get("hpc_client", (None, None) )[1]

    @property
    def is_synced(self):
        return (self.enacted is not None) and (self.enacted >= self.updated)

    @is_synced.setter
    def is_synced(self, value):
        pass

    def manage_vbng(self):
        # Each vCPE object owns exactly one vBNG object

        if self.deleted:
            return

        if self.vbng is None:
            vbngServices = VBNGService.get_service_objects().all()
            if not vbngServices:
                raise XOSConfigurationError("No VBNG Services available")

            vbng = VBNGTenant(provider_service = vbngServices[0],
                              subscriber_tenant = self)
            vbng.caller = self.creator
            vbng.save()

    def cleanup_vbng(self):
        if self.vbng:
            # print "XXX cleanup vnbg", self.vbng
            self.vbng.delete()

    def cleanup_orphans(self):
        # ensure vCPE only has one vBNG
        cur_vbng = self.vbng
        for vbng in list(self.get_subscribed_tenants(VBNGTenant)):
            if (not cur_vbng) or (vbng.id != cur_vbng.id):
                # print "XXX clean up orphaned vbng", vbng
                vbng.delete()

        if self.orig_instance_id and (self.orig_instance_id != self.get_attribute("instance_id")):
            instances=Instance.objects.filter(id=self.orig_instance_id)
            if instances:
                # print "XXX clean up orphaned instance", instances[0]
                instances[0].delete()

    def get_slice(self):
        if not self.provider_service.slices.count():
            raise XOSConfigurationError("The service has no slices")
        slice = self.provider_service.slices.all()[0]
        return slice

    def get_vsg_service(self):
        return VSGService.get_service_objects().get(id=self.provider_service.id)

    def find_instance_for_s_tag(self, s_tag):
        #s_tags = STagBlock.objects.find(s_s_tag)
        #if s_tags:
        #    return s_tags[0].instance

        tags = Tag.objects.filter(name="s_tag", value=s_tag)
        if tags:
            return tags[0].content_object

        return None

    def find_or_make_instance_for_s_tag(self, s_tag):
        instance = self.find_instance_for_s_tag(self.volt.s_tag)
        if instance:
            return instance

        flavors = Flavor.objects.filter(name="m1.small")
        if not flavors:
            raise XOSConfigurationError("No m1.small flavor")

        slice = self.provider_service.slices.all()[0]

        if slice.default_isolation == "container_vm":
            (node, parent) = ContainerVmScheduler(slice).pick()
        else:
            (node, parent) = LeastLoadedNodeScheduler(slice, label=self.get_vsg_service().node_label).pick()

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

    def manage_container(self):
        from core.models import Instance, Flavor

        if self.deleted:
            return

        # For container or container_vm isolation, use what TenantWithCotnainer
        # provides us
        slice = self.get_slice()
        if slice.default_isolation in ["container_vm", "container"]:
            super(VSGTenant,self).manage_container()
            return

        if not self.volt:
            raise XOSConfigurationError("This vCPE container has no volt")

        if self.instance:
            # We're good.
            return

        instance = self.find_or_make_instance_for_s_tag(self.volt.s_tag)
        self.instance = instance
        super(TenantWithContainer, self).save()

    def cleanup_container(self):
        if self.get_slice().default_isolation in ["container_vm", "container"]:
            super(VSGTenant,self).cleanup_container()

        # To-do: cleanup unused instances
        pass

    def manage_bbs_account(self):
        if self.deleted:
            return

        if self.volt and self.volt.subscriber and self.volt.subscriber.url_filter_enable:
            if not self.bbs_account:
                # make sure we use the proxied VSGService object, not the generic Service object
                vcpe_service = VSGService.objects.get(id=self.provider_service.id)
                self.bbs_account = vcpe_service.allocate_bbs_account()
                super(VSGTenant, self).save()
        else:
            if self.bbs_account:
                self.bbs_account = None
                super(VSGTenant, self).save()

    def get_wan_address_from_pool(self):
        ap = AddressPool.objects.filter(name="public_addresses")
        if not ap:
            raise Exception("AddressPool 'public_addresses' does not exist. Please configure it.")
        ap = ap[0]

        addr = ap.get_address()
        if not addr:
            raise Exception("AddressPool 'public_addresses' has run out of addresses.")
        return addr

    def put_wan_address_to_pool(self, addr):
        AddressPool.objects.filter(name="public_addresses")[0].put_address(addr)

    def manage_wan_container_ip(self):
        if CORD_USE_VTN:
            if not self.wan_container_ip:
                addr = self.get_wan_address_from_pool()

                self.wan_container_ip = addr
                super(TenantWithContainer, self).save()

    def cleanup_wan_container_ip(self):
        if CORD_USE_VTN and self.wan_container_ip:
            self.put_wan_address_to_pool(self.wan_container_ip)
            self.wan_container_ip = None

    def find_or_make_port(self, instance, network, **kwargs):
        port = Port.objects.filter(instance=instance, network=network)
        if port:
            port = port[0]
        else:
            port = Port(instance=instance, network=network, **kwargs)
            port.save()
        return port

    def get_lan_network(self, instance):
        slice = self.provider_service.slices.all()[0]
        if CORD_USE_VTN:
            # there should only be one network private network, and its template should not be the management template
            lan_networks = [x for x in slice.networks.all() if x.template.visibility=="private" and (not "management" in x.template.name)]
            if len(lan_networks)>1:
                raise XOSProgrammingError("The vSG slice should only have one non-management private network")
        else:
            lan_networks = [x for x in slice.networks.all() if "lan" in x.name]
        if not lan_networks:
            raise XOSProgrammingError("No lan_network")
        return lan_networks[0]

    def save_instance(self, instance):
        with transaction.atomic():
            instance.volumes = "/etc/dnsmasq.d,/etc/ufw"
            super(VSGTenant, self).save_instance(instance)

            if instance.isolation in ["container", "container_vm"]:
                lan_network = self.get_lan_network(instance)
                port = self.find_or_make_port(instance, lan_network, ip="192.168.0.1", port_id="unmanaged")
                port.set_parameter("c_tag", self.volt.c_tag)
                port.set_parameter("s_tag", self.volt.s_tag)
                port.set_parameter("device", "eth1")
                port.set_parameter("bridge", "br-lan")

                wan_networks = [x for x in instance.slice.networks.all() if "wan" in x.name]
                if not wan_networks:
                    raise XOSProgrammingError("No wan_network")
                port = self.find_or_make_port(instance, wan_networks[0])
                port.set_parameter("next_hop", value="10.0.1.253")   # FIX ME
                port.set_parameter("device", "eth0")

            if instance.isolation in ["vm"]:
                lan_network = self.get_lan_network(instance)
                port = self.find_or_make_port(instance, lan_network)
                port.set_parameter("c_tag", self.volt.c_tag)
                port.set_parameter("s_tag", self.volt.s_tag)
                port.set_parameter("neutron_port_name", "stag-%s" % self.volt.s_tag)
                port.save()

            # tag the instance with the s-tag, so we can easily find the
            # instance later
            if self.volt and self.volt.s_tag:
                tags = Tag.objects.filter(name="s_tag", value=self.volt.s_tag)
                if not tags:
                    tag = Tag(service=self.provider_service, content_object=instance, name="s_tag", value=self.volt.s_tag)
                    tag.save()

            # VTN-CORD needs a WAN address for the VM, so that the VM can
            # be configured.
            if CORD_USE_VTN:
                tags = Tag.select_by_content_object(instance).filter(name="vm_wan_addr")
                if not tags:
                    address = self.get_wan_address_from_pool()
                    tag = Tag(service=self.provider_service, content_object=instance, name="vm_wan_addr", value="%s,%s,%s" % ("public_addresses", address, self.ip_to_mac(address)))
                    tag.save()

    def save(self, *args, **kwargs):
        if not self.creator:
            if not getattr(self, "caller", None):
                # caller must be set when creating a vCPE since it creates a slice
                raise XOSProgrammingError("VSGTenant's self.caller was not set")
            self.creator = self.caller
            if not self.creator:
                raise XOSProgrammingError("VSGTenant's self.creator was not set")

        super(VSGTenant, self).save(*args, **kwargs)
        model_policy_vcpe(self.pk)

    def delete(self, *args, **kwargs):
        self.cleanup_vbng()
        self.cleanup_container()
        self.cleanup_wan_container_ip()
        super(VSGTenant, self).delete(*args, **kwargs)

def model_policy_vcpe(pk):
    # TODO: this should be made in to a real model_policy
    with transaction.atomic():
        vcpe = VSGTenant.objects.select_for_update().filter(pk=pk)
        if not vcpe:
            return
        vcpe = vcpe[0]
        vcpe.manage_wan_container_ip()
        vcpe.manage_container()
        vcpe.manage_vbng()
        vcpe.manage_bbs_account()
        vcpe.cleanup_orphans()

#----------------------------------------------------------------------------
# vBNG
#----------------------------------------------------------------------------

class VBNGService(Service):
    KIND = VBNG_KIND

    simple_attributes = ( ("vbng_url", ""), )  # "http://10.0.3.136:8181/onos/virtualbng/"

    class Meta:
        app_label = "cord"
        verbose_name = "vBNG Service"
        proxy = True

VBNGService.setup_simple_attributes()

class VBNGTenant(Tenant):
    class Meta:
        proxy = True

    KIND = VBNG_KIND

    default_attributes = {"routeable_subnet": "",
                          "mapped_ip": "",
                          "mapped_mac": "",
                          "mapped_hostname": ""}

    @property
    def routeable_subnet(self):
        return self.get_attribute("routeable_subnet", self.default_attributes["routeable_subnet"])

    @routeable_subnet.setter
    def routeable_subnet(self, value):
        self.set_attribute("routeable_subnet", value)

    @property
    def mapped_ip(self):
        return self.get_attribute("mapped_ip", self.default_attributes["mapped_ip"])

    @mapped_ip.setter
    def mapped_ip(self, value):
        self.set_attribute("mapped_ip", value)

    @property
    def mapped_mac(self):
        return self.get_attribute("mapped_mac", self.default_attributes["mapped_mac"])

    @mapped_mac.setter
    def mapped_mac(self, value):
        self.set_attribute("mapped_mac", value)

    @property
    def mapped_hostname(self):
        return self.get_attribute("mapped_hostname", self.default_attributes["mapped_hostname"])

    @mapped_hostname.setter
    def mapped_hostname(self, value):
        self.set_attribute("mapped_hostname", value)
