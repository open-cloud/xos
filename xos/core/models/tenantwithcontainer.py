
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
from tenantwithcontainer_decl import *

class TenantWithContainer(TenantWithContainer_decl):
    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super(TenantWithContainer, self).__init__(*args, **kwargs)

        # vSG service relies on knowing when instance id has changed
        self.orig_instance_id = self.get_attribute("instance_id")

    # vSG service relies on instance_id attribute
    def get_attribute(self, name, default=None):
        if name=="instance_id":
            if self.instance:
                return self.instance.id
            else:
                return None
        else:
            return super(TenantWithContainer, self).get_attribute(name, default)

    # Services may wish to override the image() function to return different
    # images based on criteria in the tenant object. For example,
    #    if (self.has_feature_A):
    #        return Instance.object.get(name="image_with_feature_a")
    #    elif (self.has_feature_B):
    #        return Instance.object.get(name="image_with_feature_b")
    #    else:
    #        return super(MyTenantClass,self).image()

    @property
    def image(self):
        from core.models import Image
        # Implement the logic here to pick the image that should be used when
        # instantiating the VM that will hold the container.

        slice = self.provider_service.slices.all()
        if not slice:
            raise XOSProgrammingError("provider service has no slice")
        slice = slice[0]

        # If slice has default_image set then use it
        if slice.default_image:
            return slice.default_image

        raise XOSProgrammingError("Please set a default image for %s" % self.slice.name)

    def save(self, *args, **kwargs):
        if (not self.creator) and (hasattr(self, "caller")) and (self.caller):
            self.creator = self.caller

        super(TenantWithContainer, self).save(*args, **kwargs)

