
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

def save_instance(self, instance):
    # Override this function to do custom pre-save or post-save processing,
    # such as creating ports for containers.
    instance.save()

def pick_least_loaded_instance_in_slice(self, slices, image):
    for slice in slices:
        if slice.instances.all().count() > 0:
            for instance in slice.instances.all():
                if instance.image != image:
                    continue
                # Pick the first instance that has lesser than 5 tenants
                if self.count_of_tenants_of_an_instance(instance) < 5:
                    return instance
    return None

# TODO: Ideally the tenant count for an instance should be maintained using a
# many-to-one relationship attribute, however this model being proxy, it does
# not permit any new attributes to be defined. Find if any better solutions
def count_of_tenants_of_an_instance(self, instance):
    tenant_count = 0
    for tenant in self.__class__.objects.all():
        if tenant.get_attribute("instance_id", None) == instance.id:
            tenant_count += 1
    return tenant_count

def manage_container(self):
    from core.models import Instance, Flavor

    if self.deleted:
        return

    if (self.instance is not None) and (self.instance.image != self.image):
        self.instance.delete()
        self.instance = None

    if self.instance is None:
        if not self.provider_service.slices.count():
            raise XOSConfigurationError("The service has no slices")

        new_instance_created = False
        instance = None
        if self.get_attribute("use_same_instance_for_multiple_tenants", default=False):
            # Find if any existing instances can be used for this tenant
            slices = self.provider_service.slices.all()
            instance = self.pick_least_loaded_instance_in_slice(slices, self.image)

        if not instance:
            slice = self.provider_service.slices.all()[0]

            flavor = slice.default_flavor
            if not flavor:
                flavors = Flavor.objects.filter(name="m1.small")
                if not flavors:
                    raise XOSConfigurationError("No m1.small flavor")
                flavor = flavors[0]

            if slice.default_isolation == "container_vm":
                (node, parent) = ContainerVmScheduler(slice).pick()
            else:
                (node, parent) = LeastLoadedNodeScheduler(slice).pick()

            instance = Instance(slice=slice,
                                node=node,
                                image=self.image,
                                creator=self.creator,
                                deployment=node.site_deployment.deployment,
                                flavor=flavor,
                                isolation=slice.default_isolation,
                                parent=parent)
            self.save_instance(instance)
            new_instance_created = True

        try:
            self.instance = instance
            super(TenantWithContainer, self).save()
        except:
            if new_instance_created:
                instance.delete()
            raise

def cleanup_container(self):
    if self.instance:
        if self.get_attribute("use_same_instance_for_multiple_tenants", default=False):
            # Delete the instance only if this is last tenant in that
            # instance
            tenant_count = self.count_of_tenants_of_an_instance(
                self.instance)
            if tenant_count == 0:
                self.instance.delete()
        else:
            self.instance.delete()
        self.instance = None

def __xos_save_base(self, *args, **kwargs):
    if (not self.creator) and (hasattr(self, "caller")) and (self.caller):
        self.creator = self.caller

