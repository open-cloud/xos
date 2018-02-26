
# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from xos.exceptions import *
from serviceinstance_decl import *

class ServiceInstance(ServiceInstance_decl):
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(ServiceInstance, self).__init__(*args, **kwargs)

    @property
    def tenantattribute_dict(self):
        attrs = {}
        for attr in self.tenantattributes.all():
            attrs[attr.name] = attr.value
        return attrs

    # helper function to be used in subclasses that want to ensure
    # service_specific_id is unique

    def validate_unique_service_specific_id(self, none_okay=False):
        if not none_okay and (self.service_specific_id is None):
            raise XOSMissingField("subscriber_specific_id is None, and it's a required field", fields={
                                  "service_specific_id": "cannot be none"})

        if self.service_specific_id:
            conflicts = self.__class__.objects.filter(
                service_specific_id=self.service_specific_id)
            if self.pk:
                conflicts = conflicts.exclude(pk=self.pk)
            if conflicts:
                raise XOSDuplicateKey("service_specific_id %s already exists" % self.service_specific_id, fields={
                                      "service_specific_id": "duplicate key"})

    def get_subscribed_tenants(self, tenant_class):
        """ Return all ServiceInstances of class tenant_class that have a link to this ServiceInstance """
        results=[]
        # TODO: Make query more efficient
        for si in tenant_class.objects.all():
            for link in si.subscribed_links.all():
                if link.provider_service_instance == self:
                    results.append(si)
        return results

    def get_newest_subscribed_tenant(self, kind):
        st = list(self.get_subscribed_tenants(kind))
        if not st:
            return None
        return sorted(st, key=attrgetter('id'))[0]

    def save(self, *args, **kwargs):
        if hasattr(self, "OWNER_CLASS_NAME"):
            owner_class = self.get_model_class_by_name(self.OWNER_CLASS_NAME)
            if not owner_class:
                raise XOSValidationError("Cannot find owner class %s" % self.OWNER_CLASS_NAME)

            need_set_owner = True
            if self.owner_id:
                # Check to see if owner is set to a valid instance of owner_class. If it is, then we already have an
                # owner. If it is not, then some other misbehaving class must have altered the ServiceInstance.meta
                # to point to its own default (these services are being cleaned up).
                if owner_class.objects.filter(id=self.owner_id).exists():
                    need_set_owner = False

            if need_set_owner:
                owners = owner_class.objects.all()
                if not owners:
                    raise XOSValidationError("Cannot find eligible owner of class %s" % self.OWNER_CLASS_NAME)

                self.owner = owners[0]
        else:
            # Deal with legacy services that specify their owner as _meta field default. This is a workaround for
            # what is probably a django bug (if a SerivceInstance without a default is created before a ServiceInstance
            # that does have a default, then the later service's default is not honored by django).

            # TODO: Delete this after all services have been migrated away from using field defaults

            if (not self.owner_id) and (self._meta.get_field("owner").default):
                self.owner = Service.objects.get(id = self._meta.get_field("owner").default)

        # If the model has a Creator and it's not specified, then attempt to default to the Caller. Caller is
        # automatically filled in my the API layer. This code was typically used by ServiceInstances that lead to
        # instance creation.
        if (hasattr(self, "creator")) and (not self.creator) and (hasattr(self, "caller")) and (self.caller):
            self.creator = self.caller

        super(ServiceInstance, self).save(*args, **kwargs)


