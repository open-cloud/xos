from django.db import models
from core.models import PlCoreBase,SingletonModel,PlCoreBaseManager
from core.models.plcorebase import StrippedCharField
from xos.exceptions import *
from operator import attrgetter
import json

COARSE_KIND="coarse"

class AttributeMixin(object):
    # helper for extracting things from a json-encoded service_specific_attribute
    def get_attribute(self, name, default=None):
        if self.service_specific_attribute:
            attributes = json.loads(self.service_specific_attribute)
        else:
            attributes = {}
        return attributes.get(name, default)

    def set_attribute(self, name, value):
        if self.service_specific_attribute:
            attributes = json.loads(self.service_specific_attribute)
        else:
            attributes = {}
        attributes[name]=value
        self.service_specific_attribute = json.dumps(attributes)

    def get_initial_attribute(self, name, default=None):
        if self._initial["service_specific_attribute"]:
            attributes = json.loads(self._initial["service_specific_attribute"])
        else:
            attributes = {}
        return attributes.get(name, default)

    @classmethod
    def setup_simple_attributes(cls):
        for (attrname, default) in cls.simple_attributes:
            setattr(cls, attrname, property(lambda self, attrname=attrname, default=default: self.get_attribute(attrname, default),
                                            lambda self, value, attrname=attrname: self.set_attribute(attrname, value),
                                            None,
                                            attrname))

class Service(PlCoreBase, AttributeMixin):
    # when subclassing a service, redefine KIND to describe the new service
    KIND = "generic"

    description = models.TextField(max_length=254,null=True, blank=True,help_text="Description of Service")
    enabled = models.BooleanField(default=True)
    kind = StrippedCharField(max_length=30, help_text="Kind of service", default=KIND)
    name = StrippedCharField(max_length=30, help_text="Service Name")
    versionNumber = StrippedCharField(max_length=30, help_text="Version of Service Definition")
    published = models.BooleanField(default=True)
    view_url = StrippedCharField(blank=True, null=True, max_length=1024)
    icon_url = StrippedCharField(blank=True, null=True, max_length=1024)
    public_key = models.TextField(null=True, blank=True, max_length=1024, help_text="Public key string")
    private_key_fn = StrippedCharField(blank=True, null=True, max_length=1024)

    # Service_specific_attribute and service_specific_id are opaque to XOS
    service_specific_id = StrippedCharField(max_length=30, blank=True, null=True)
    service_specific_attribute = models.TextField(blank=True, null=True)

    def __init__(self, *args, **kwargs):
        # for subclasses, set the default kind appropriately
        self._meta.get_field("kind").default = self.KIND
        super(Service, self).__init__(*args, **kwargs)

    @classmethod
    def get_service_objects(cls):
        return cls.objects.filter(kind = cls.KIND)

    @classmethod
    def get_deleted_service_objects(cls):
        return cls.deleted_objects.filter(kind = cls.KIND)

    @classmethod
    def get_service_objects_by_user(cls, user):
        return cls.select_by_user(user).filter(kind = cls.KIND)

    @classmethod
    def select_by_user(cls, user):
        if user.is_admin:
            return cls.objects.all()
        else:
            service_ids = [sp.slice.id for sp in ServicePrivilege.objects.filter(user=user)]
            return cls.objects.filter(id__in=service_ids)

    def __unicode__(self): return u'%s' % (self.name)

    def can_update(self, user):
        return user.can_update_service(self, allow=['admin'])

    def get_scalable_nodes(self, slice, max_per_node=None, exclusive_slices=[]):
        """
             Get a list of nodes that can be used to scale up a slice.

                slice - slice to scale up
                max_per_node - maximum numbers of instances that 'slice' can have on a single node
                exclusive_slices - list of slices that must have no nodes in common with 'slice'.
        """

        from core.models import Node, Instance # late import to get around order-of-imports constraint in __init__.py

        nodes = list(Node.objects.all())

        conflicting_instances = Instance.objects.filter(slice__in = exclusive_slices)
        conflicting_nodes = Node.objects.filter(instances__in = conflicting_instances)

        nodes = [x for x in nodes if x not in conflicting_nodes]

        # If max_per_node is set, then limit the number of instances this slice
        # can have on a single node.
        if max_per_node:
            acceptable_nodes = []
            for node in nodes:
                existing_count = node.instances.filter(slice=slice).count()
                if existing_count < max_per_node:
                    acceptable_nodes.append(node)
            nodes = acceptable_nodes

        return nodes

    def pick_node(self, slice, max_per_node=None, exclusive_slices=[]):
        # Pick the best node to scale up a slice.

        nodes = self.get_scalable_nodes(slice, max_per_node, exclusive_slices)
        nodes = sorted(nodes, key=lambda node: node.instances.all().count())
        if not nodes:
            return None
        return nodes[0]

    def adjust_scale(self, slice_hint, scale, max_per_node=None, exclusive_slices=[]):
        from core.models import Instance # late import to get around order-of-imports constraint in __init__.py

        slices = [x for x in self.slices.all() if slice_hint in x.name]
        for slice in slices:
            while slice.instances.all().count() > scale:
                s = slice.instances.all()[0]
                # print "drop instance", s
                s.delete()

            while slice.instances.all().count() < scale:
                node = self.pick_node(slice, max_per_node, exclusive_slices)
                if not node:
                    # no more available nodes
                    break

                image = slice.default_image
                if not image:
                    raise XOSConfigurationError("No default_image for slice %s" % slice.name)

                flavor = slice.default_flavor
                if not flavor:
                    raise XOSConfigurationError("No default_flavor for slice %s" % slice.name)

                s = Instance(slice=slice,
                           node=node,
                           creator=slice.creator,
                           image=image,
                           flavor=flavor,
                           deployment=node.site_deployment.deployment)
                s.save()

                # print "add instance", s

class ServiceAttribute(PlCoreBase):
    name = models.SlugField(help_text="Attribute Name", max_length=128)
    value = StrippedCharField(help_text="Attribute Value", max_length=1024)
    service = models.ForeignKey(Service, related_name='serviceattributes', help_text="The Service this attribute is associated with")

class ServiceRole(PlCoreBase):
    ROLE_CHOICES = (('admin','Admin'),)
    role = StrippedCharField(choices=ROLE_CHOICES, unique=True, max_length=30)

    def __unicode__(self):  return u'%s' % (self.role)

class ServicePrivilege(PlCoreBase):
    user = models.ForeignKey('User', related_name='serviceprivileges')
    service = models.ForeignKey('Service', related_name='serviceprivileges')
    role = models.ForeignKey('ServiceRole',related_name='serviceprivileges')

    class Meta:
        unique_together =  ('user', 'service', 'role')

    def __unicode__(self):  return u'%s %s %s' % (self.service, self.user, self.role)

    def can_update(self, user):
        if not self.service.enabled:
            raise PermissionDenied, "Cannot modify permission(s) of a disabled service"
        return self.service.can_update(user)

    def save(self, *args, **kwds):
        if not self.service.enabled:
            raise PermissionDenied, "Cannot modify permission(s) of a disabled service"
        super(ServicePrivilege, self).save(*args, **kwds)

    def delete(self, *args, **kwds):
        if not self.service.enabled:
            raise PermissionDenied, "Cannot modify permission(s) of a disabled service"
        super(ServicePrivilege, self).delete(*args, **kwds)

    @classmethod
    def select_by_user(cls, user):
        if user.is_admin:
            qs = cls.objects.all()
        else:
            qs = cls.objects.filter(user=user)
        return qs

class TenantRoot(PlCoreBase, AttributeMixin):
    """ A tenantRoot is one of the things that can sit at the root of a chain
        of tenancy. This object represents a node.
    """

    KIND= "generic"
    kind = StrippedCharField(max_length=30, default=KIND)
    name = StrippedCharField(max_length=255, help_text="name", blank=True, null=True)

    service_specific_attribute = models.TextField(blank=True, null=True)
    service_specific_id = StrippedCharField(max_length=30, blank=True, null=True)

    def __init__(self, *args, **kwargs):
        # for subclasses, set the default kind appropriately
        self._meta.get_field("kind").default = self.KIND
        super(TenantRoot, self).__init__(*args, **kwargs)

    def __unicode__(self):
        if not self.name:
            return u"%s-tenant_root-#%s" % (str(self.kind), str(self.id))
        else:
            return self.name

    def can_update(self, user):
        return user.can_update_tenant_root(self, allow=['admin'])

    def get_subscribed_tenants(self, tenant_class):
        ids = self.subscribed_tenants.filter(kind=tenant_class.KIND)
        return tenant_class.objects.filter(id__in = ids)

    def get_newest_subscribed_tenant(self, kind):
        st = list(self.get_subscribed_tenants(kind))
        if not st:
            return None
        return sorted(st, key=attrgetter('id'))[0]

    @classmethod
    def get_tenant_objects(cls):
        return cls.objects.filter(kind = cls.KIND)

    @classmethod
    def get_tenant_objects_by_user(cls, user):
        return cls.select_by_user(user).filter(kind = cls.KIND)

    @classmethod
    def select_by_user(cls, user):
        if user.is_admin:
            return cls.objects.all()
        else:
            tr_ids = [trp.tenant_root.id for trp in TenantRootPrivilege.objects.filter(user=user)]
            return cls.objects.filter(id__in=tr_ids)

class Tenant(PlCoreBase, AttributeMixin):
    """ A tenant is a relationship between two entities, a subscriber and a
        provider. This object represents an edge.

        The subscriber can be a User, a Service, or a Tenant.

        The provider is always a Service.

        TODO: rename "Tenant" to "Tenancy"
    """

    CONNECTIVITY_CHOICES = (('public', 'Public'), ('private', 'Private'), ('na', 'Not Applicable'))

    # when subclassing a service, redefine KIND to describe the new service
    KIND = "generic"

    kind = StrippedCharField(max_length=30, default=KIND)
    provider_service = models.ForeignKey(Service, related_name='provided_tenants')

    # The next four things are the various type of objects that can be subscribers of this Tenancy
    # relationship. One and only one can be used at a time.
    subscriber_service = models.ForeignKey(Service, related_name='subscribed_tenants', blank=True, null=True)
    subscriber_tenant = models.ForeignKey("Tenant", related_name='subscribed_tenants', blank=True, null=True)
    subscriber_user = models.ForeignKey("User", related_name='subscribed_tenants', blank=True, null=True)
    subscriber_root = models.ForeignKey("TenantRoot", related_name="subscribed_tenants", blank=True, null=True)

    # Service_specific_attribute and service_specific_id are opaque to XOS
    service_specific_id = StrippedCharField(max_length=30, blank=True, null=True)
    service_specific_attribute = models.TextField(blank=True, null=True)

    # Connect_method is only used by Coarse tenants
    connect_method = models.CharField(null=False, blank=False, max_length=30, choices=CONNECTIVITY_CHOICES, default="na")

    def __init__(self, *args, **kwargs):
        # for subclasses, set the default kind appropriately
        self._meta.get_field("kind").default = self.KIND
        super(Tenant, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return u"%s-tenant-%s" % (str(self.kind), str(self.id))

    @classmethod
    def get_tenant_objects(cls):
        return cls.objects.filter(kind = cls.KIND)

    @classmethod
    def get_tenant_objects_by_user(cls, user):
        return cls.select_by_user(user).filter(kind = cls.KIND)

    @classmethod
    def get_deleted_tenant_objects(cls):
        return cls.deleted_objects.filter(kind = cls.KIND)

    # helper function to be used in subclasses that want to ensure service_specific_id is unique
    def validate_unique_service_specific_id(self):
        if self.pk is None:
            if self.service_specific_id is None:
                raise XOSMissingField("subscriber_specific_id is None, and it's a required field", fields={"service_specific_id": "cannot be none"})

            conflicts = self.get_tenant_objects().filter(service_specific_id=self.service_specific_id)
            if conflicts:
                raise XOSDuplicateKey("service_specific_id %s already exists" % self.service_specific_id, fields={"service_specific_id": "duplicate key"})

    def save(self, *args, **kwargs):
        subCount = sum( [1 for e in [self.subscriber_service, self.subscriber_tenant, self.subscriber_user, self.subscriber_root] if e is not None])
        if (subCount > 1):
            raise XOSConflictingField("Only one of subscriber_service, subscriber_tenant, subscriber_user, subscriber_root should be set")

        super(Tenant, self).save(*args, **kwargs)

    def get_subscribed_tenants(self, tenant_class):
        ids = self.subscribed_tenants.filter(kind=tenant_class.KIND)
        return tenant_class.objects.filter(id__in = ids)

    def get_newest_subscribed_tenant(self, kind):
        st = list(self.get_subscribed_tenants(kind))
        if not st:
            return None
        return sorted(st, key=attrgetter('id'))[0]

class TenantWithContainer(Tenant):
    """ A tenant that manages a container """

    # this is a hack and should be replaced by something smarter...
    LOOK_FOR_IMAGES=["ubuntu-vcpe4",        # ONOS demo machine -- preferred vcpe image
                     "Ubuntu 14.04 LTS",    # portal
                     "Ubuntu-14.04-LTS",    # ONOS demo machine
                     "trusty-server-multi-nic", # CloudLab
                    ]

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(TenantWithContainer, self).__init__(*args, **kwargs)
        self.cached_instance=None
        self.orig_instance_id = self.get_initial_attribute("instance_id")
#        self.cached_container=None
#        self.orig_container_id = self.get_initial_attribute("container_id")


    @property
    def instance(self):
        from core.models import Instance
        if getattr(self, "cached_instance", None):
            return self.cached_instance
        instance_id=self.get_attribute("instance_id")
        if not instance_id:
            return None
        instances=Instance.objects.filter(id=instance_id)
        if not instances:
            return None
        instance=instances[0]
        instance.caller = self.creator
        self.cached_instance = instance
        return instance

    @instance.setter
    def instance(self, value):
        if value:
            value = value.id
        if (value != self.get_attribute("instance_id", None)):
            self.cached_instance=None
        self.set_attribute("instance_id", value)

#    @property
#    def container(self):
#        from core.models import Container
#        if getattr(self, "cached_container", None):
#            return self.cached_container
#        container_id=self.get_attribute("container_id")
#        if not container_id:
#            return None
#        containers=Container.objects.filter(id=container_id)
#        if not containers:
#            return None
#        container=containers[0]
#        container.caller = self.creator
#        self.cached_container = container
#        return container
#
#    @container.setter
#    def container(self, value):
#        if value:
#            value = value.id
#        if (value != self.get_attribute("container_id", None)):
#            self.cached_container=None
#        self.set_attribute("container_id", value)

    @property
    def creator(self):
        from core.models import User
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

    @property
    def image(self):
        from core.models import Image
        # Implement the logic here to pick the image that should be used when
        # instantiating the VM that will hold the container.
        for image_name in self.LOOK_FOR_IMAGES:
            images = Image.objects.filter(name = image_name)
            if images:
                return images[0]

        raise XOSProgrammingError("No VPCE image (looked for %s)" % str(self.LOOK_FOR_IMAGES))

    @property
    def use_cobm(self):
        return self.get_attribute("use_cobm", False)

    @use_cobm.setter
    def use_cobm(self, v):
        self.set_attribute("use_cobm", v)

    @creator.setter
    def creator(self, value):
        if value:
            value = value.id
        if (value != self.get_attribute("creator_id", None)):
            self.cached_creator=None
        self.set_attribute("creator_id", value)

    def pick_node_for_instance(self):
        from core.models import Node
        nodes = list(Node.objects.all())
        # TODO: logic to filter nodes by which nodes are up, and which
        #   nodes the slice can instantiate on.
        nodes = sorted(nodes, key=lambda node: node.instances.all().count())
        return nodes[0]

#    def pick_node_for_container_on_metal(self):
#        from core.models import Node
#        nodes = list(Node.objects.all())
#        # TODO: logic to filter nodes by which nodes are up, and which
#        #   nodes the slice can instantiate on.
#        nodes = sorted(nodes, key=lambda node: node.containers.all().count())
#        return nodes[0]

    def manage_container_in_instance(self):
        from core.models import Instance, Flavor

        if self.deleted:
            return

        if (self.instance is not None) and (self.instance.image != self.image):
            self.instance.delete()
            self.instance = None

        if self.instance is None:
            if not self.provider_service.slices.count():
                raise XOSConfigurationError("The VCPE service has no slices")

            flavors = Flavor.objects.filter(name="m1.small")
            if not flavors:
                raise XOSConfigurationError("No m1.small flavor")

            node =self.pick_node_for_instance()
            instance = Instance(slice = self.provider_service.slices.all()[0],
                            node = node,
                            image = self.image,
                            creator = self.creator,
                            deployment = node.site_deployment.deployment,
                            flavor = flavors[0])
            instance.save()

            try:
                self.instance = instance
                super(TenantWithContainer, self).save()
            except:
                instance.delete()
                raise

#    def manage_container_on_metal(self):
#        from core.models import Container, Instance, Flavor, Port
#
#        if self.deleted:
#            return
#
#        if (self.container is not None):
#            self.container.delete()
#            self.container = None
#
#        if self.container is None:
#            if not self.provider_service.slices.count():
#                raise XOSConfigurationError("The VCPE service has no slices")
#
#            slice = self.provider_service.slices.all()[0]
#            node = self.pick_node_for_container_on_metal()
#
#            # Our current docker network strategy requires that there be some
#            # instance on the server that connects to the networks, so that
#            # the containers can piggyback off of that configuration.
#            instances = Instance.objects.filter(slice=slice, node=node)
#            if not instances:
#                flavors = Flavor.objects.filter(name="m1.small")
#                if not flavors:
#                    raise XOSConfigurationError("No m1.small flavor")
#
#                node =self.pick_node_for_instance()
#                instance = Instance(slice = self.provider_service.slices.all()[0],
#                                node = node,
#                                image = self.image,
#                                creator = self.creator,
#                                deployment = node.site_deployment.deployment,
#                                flavor = flavors[0])
#                instance.save()
#
#            # Now make the container...
#            container = Container(slice = slice,
#                            node = node,
#                            docker_image = "andybavier/docker-vcpe",
#                            creator = self.creator,
#                            no_sync=True)
#            container.save()
#
#            # ... and add the ports for the container
#            # XXX probably should be done in model_policy
#            for network in slice.networks.all():
#                if (network.name.endswith("-nat")):
#                    continue
#                port = Port(network = network,
#                            container = container)
#                port.save()
#
#            container.no_sync = False
#            container.save()
#
#            try:
#                self.container = container
#                super(TenantWithContainer, self).save()
#            except:
#                container.delete()
#                raise

    def manage_container(self):
#        if self.use_cobm:
#            self.manage_container_on_metal()
#        else:
            self.manage_container_in_instance()

    def cleanup_container(self):
        if self.instance:
            # print "XXX cleanup instance", self.instance
            self.instance.delete()
            self.instance = None
#        if self.container:
#            # print "XXX cleanup container", self.container
#            self.container.delete()
#            self.container = None

class CoarseTenant(Tenant):
    """ TODO: rename "CoarseTenant" --> "StaticTenant" """
    class Meta:
        proxy = True

    KIND = COARSE_KIND

    def save(self, *args, **kwargs):
        if (not self.subscriber_service):
            raise XOSValidationError("subscriber_service cannot be null")
        if (self.subscriber_tenant or self.subscriber_user):
            raise XOSValidationError("subscriber_tenant and subscriber_user must be null")

        super(CoarseTenant,self).save()

class Subscriber(TenantRoot):
    """ Intermediate class for TenantRoots that are to be Subscribers """

    class Meta:
        proxy = True

    KIND = "Subscriber"

class Provider(TenantRoot):
    """ Intermediate class for TenantRoots that are to be Providers """

    class Meta:
        proxy = True

    KIND = "Provider"

class TenantAttribute(PlCoreBase):
    name = models.CharField(help_text="Attribute Name", max_length=128)
    value = models.TextField(help_text="Attribute Value")
    tenant = models.ForeignKey(Tenant, related_name='tenantattributes', help_text="The Tenant this attribute is associated with")

class TenantRootRole(PlCoreBase):
    ROLE_CHOICES = (('admin','Admin'), ('access','Access'))

    role = StrippedCharField(choices=ROLE_CHOICES, unique=True, max_length=30)

    def __unicode__(self):  return u'%s' % (self.role)

class TenantRootPrivilege(PlCoreBase):
    user = models.ForeignKey('User', related_name="tenant_root_privileges")
    tenant_root = models.ForeignKey('TenantRoot', related_name="tenant_root_privileges")
    role = models.ForeignKey('TenantRootRole', related_name="tenant_root_privileges")

    class Meta:
        unique_together = ('user', 'tenant_root', 'role')

    def __unicode__(self):  return u'%s %s %s' % (self.tenant_root, self.user, self.role)

    def save(self, *args, **kwds):
        if not self.user.is_active:
            raise PermissionDenied, "Cannot modify role(s) of a disabled user"
        super(TenantRootPrivilege, self).save(*args, **kwds)

    def can_update(self, user):
        return user.can_update_tenant_root_privilege(self)

    @classmethod
    def select_by_user(cls, user):
        if user.is_admin:
            return cls.objects.all()
        else:
            # User can see his own privilege
            trp_ids = [trp.id for trp in cls.objects.filter(user=user)]

            # A slice admin can see the SlicePrivileges for his Slice
            for priv in cls.objects.filter(user=user, role__role="admin"):
                trp_ids.extend( [trp.id for trp in cls.objects.filter(tenant_root=priv.tenant_root)] )

            return cls.objects.filter(id__in=trp_ids)


