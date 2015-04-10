from django.db import models
from core.models import PlCoreBase,SingletonModel
from core.models.plcorebase import StrippedCharField

class Service(PlCoreBase):
    description = models.TextField(max_length=254,null=True, blank=True,help_text="Description of Service")
    enabled = models.BooleanField(default=True)
    name = StrippedCharField(max_length=30, help_text="Service Name")
    versionNumber = StrippedCharField(max_length=30, help_text="Version of Service Definition")
    published = models.BooleanField(default=True)
    view_url = StrippedCharField(blank=True, null=True, max_length=1024)
    icon_url = StrippedCharField(blank=True, null=True, max_length=1024)

    def __unicode__(self): return u'%s' % (self.name)

class ServiceAttribute(PlCoreBase):
    name = models.SlugField(help_text="Attribute Name", max_length=128)
    value = StrippedCharField(help_text="Attribute Value", max_length=1024)
    service = models.ForeignKey(Service, related_name='serviceattributes', help_text="The Service this attribute is associated with")

class Tenant(PlCoreBase):
    """ A tenant is a relationship between two entities, a subscriber and a
        provider.

        The subscriber can be a User, a Service, or a Tenant.

        The provider is always a Service.
    """
    kind = StrippedCharField(max_length=30)
    provider_service = models.ForeignKey(Service, related_name='tenants')
    subscriber_service = models.ForeignKey(Service, related_name='subscriptions', blank=True, null=True)
    subscriber_tenant = models.ForeignKey("Tenant", related_name='subscriptions', blank=True, null=True)
    subscriber_user = models.ForeignKey("User", related_name='subscriptions', blank=True, null=True)
    service_specific_id = StrippedCharField(max_length=30)
    service_specific_attribute = models.TextField()

    def __unicode__(self):
        if self.subscriber_service:
            return u'%s tenant %s on %s' % (str(self.kind), str(self.subscriber_service), str(self.provider_service))
        else:
            return u'%s tenant %s on %s' % (str(self.kind), str(self.subscriber_tenant), str(self.provider_service))

    # helper for extracting things from a json-encoded service_specific_attribute
    def get_attribute(self, name, default=None):
        if self.service_specific_attribute:
            attributes = json.loads(self.service_specific_attribute)
        else:
            attributes = {}
        return attributes.get(name, default)

    def set_attribute(self, name, value):
        if self.service_specific_attributes:
            attributes = json.loads(self.service_specific_attribute)
        else:
            attributes = {}
        attributes[name]=value
        self.service_specific_attribute = json.dumps(attributes)


