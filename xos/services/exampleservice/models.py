# models.py -  ExampleService Models

from core.models import Service, TenantWithContainer
from django.db import models, transaction

SERVICE_NAME = 'exampleservice'
SERVICE_NAME_VERBOSE = 'Example Service'
SERVICE_NAME_VERBOSE_PLURAL = 'Example Services'
TENANT_NAME_VERBOSE = 'Example Tenant'
TENANT_NAME_VERBOSE_PLURAL = 'Example Tenants'

class ExampleService(Service):

    KIND = SERVICE_NAME

    class Meta:
        app_label = SERVICE_NAME
        verbose_name = SERVICE_NAME_VERBOSE

    service_message = models.CharField(max_length=254, help_text="Service Message to Display")

class ExampleTenant(TenantWithContainer):

    KIND = SERVICE_NAME

    class Meta:
        verbose_name = TENANT_NAME_VERBOSE

    tenant_message = models.CharField(max_length=254, help_text="Tenant Message to Display")

    def __init__(self, *args, **kwargs):
        exampleservice = ExampleService.get_service_objects().all()
        if exampleservice:
            self._meta.get_field('provider_service').default = exampleservice[0].id
        super(ExampleTenant, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        super(ExampleTenant, self).save(*args, **kwargs)
        model_policy_exampletenant(self.pk)

    def delete(self, *args, **kwargs):
        self.cleanup_container()
        super(ExampleTenant, self).delete(*args, **kwargs)


def model_policy_exampletenant(pk):
    with transaction.atomic():
        tenant = ExampleTenant.objects.select_for_update().filter(pk=pk)
        if not tenant:
            return
        tenant = tenant[0]
        tenant.manage_container()

