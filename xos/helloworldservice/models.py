from core.models import Service, TenantWithContainer

HELLO_WORLD_KIND = "helloworldservice"

class HelloWorldService(Service):
    KIND = HELLO_WORLD_KIND

    class Meta:
	proxy = True
	app_label = "helloworldservice"
	verbose_name = "Hello World Service"

class HelloWorldTenant(TenantWithContainer):
    class Meta:
        proxy = True

    KIND = HELLO_WORLD_KIND
    default_attributes = {'display_message': 'Hello World!'}
    def __init__(self, *args, **kwargs):
        helloworld_services = HelloWorldService.get_service_objects().all();
	if helloworld_services:
            self._meta.get_field("provider_service").default = helloworld_services[0].id
	
	self.instance = (helloworld_services[0].slices.all()[0].instances.all()[0])
	super(HelloWorldTenant, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        super(HelloWorldTenant, self).save(*args, **kwargs)


    def delete(self, *args, **kwargs):
        self.cleanup_container()
        super(HelloWorldTenant, self).delete(*args, **kwargs)

    @property
    def display_message(self):
        return self.get_attribute(
		"display_message",
		self.default_attributes['display_message'])

    @display_message.setter
    def display_message(self, value):
        self.set_attribute("display_message", value)
