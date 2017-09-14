# CORD-4.0 Service Migration Guide

## Service/Tenancy Model Migration

CORD-4.0 makes the following changes:

- Renames `Tenant` to `ServiceInstance`.
- Replaces CORD-3.0's many-to-one tenancy links with a new many-to-many link object called `ServiceInstanceLink`. 
- Introduces the concept of service interfaces using the `InterfaceType` and `ServiceInterface` models.
- Makes `ServiceDependency` a separate model not directly related to Tenancy models. 

Note that for the purposes of this document, we still refer to some R-CORD models using the suffix "Tenant" rather than "ServiceInstance". As time permits, those R-CORD models will be renamed. New services are recommended to use the suffix ServiceInstance rather than Tenant.  

### Migrating existing Tenants

The base class has been changed from `Tenant` to `ServiceInstance`. This may require an  `xproto` change, for example:

    - message VTRTenant (Tenant){
    + message VTRTenant (ServiceInstance){

Note that `TenantWithContainer` has not yet been renamed (at some point in the future it may become `ServiceInstanceWithContainer`), so models inheriting from `TenantWithContainer` are fine for now.

### Differences in ServiceInstance fields

A few fields in ServiceInstance have been changed from what they were in `Tenant`:
 
- `Tenant.provider_service` --> `ServiceInstance.owner` 

### Creating links between Service Instances (`ServiceInstanceLink` objects)

A common pattern in CORD-3.0 model policies is to create a new Tenant and link it to an existing model. For example,

    t = VRouterTenant(provider_service=vrouter_service,
                      subscriber_tenant=some_vsg_tenant)
    t.save()

In the above example, the relationship between the new VRouterTenant and `some_vsg_tenant` was captured by the field `subscriber_tenant`. This field no longer exists in CORD-4.0 and needs to be replaced with a link:

    t = VRouterTenant(owner=vrouter_service)
    t.save()
    l = ServiceInstanceLink(provider_service_instance = t,
                            subscriber_service_interface=some_vsg_tenant)
    l.save()

### Traversing links between Service Instances

In CORD-3.0, it was possible to determine the subscriber of a Tenant by looking at the Tenant's `subscriber_*` properties. For example,

    subscriber = some_vrouter_tenant.subscriber_tenant
    vsg_tenant = VSGTenant.objects.get(id = subscriber.id)
    # now, do something with vsg_tenant

In CORD-4.0 you will need to traverse `ServiceInstanceLink` objects instead:

    for link in some_vrouter_tenant.provided_links.all():
        if link.subscriber_service_instance:
            subscriber = link.subscriber_service_instance
            vsg_tenant = subscriber.leaf_model
            # now, do something with vsg_tenant

You can also walk in the opposite direction:
    
    for link in some_vsg_tenant.subscribed_links.all():
        if link.subscriber_service_instance:
            provider = link.provider_service_instance
            vrouter_tenant = provider.leaf_model
            # now, do something with vrouter_tenant

Note that since the service instance graph now supports true many-to-many relations, it's common to have to use for loops as described above to cover cases where an object may be linked to many providers or many subscribers. If it's a known constraint that only one object may be linked, then it may be reasonable to omit the for loop and use `provided_links.first()` or `subscribed_links.first()` instead of `.all()`. 

Also note that `leaf_model` is a property that will automatically cast any base object to its descendant class. For example, if you have a generic `ServiceInstance` object, and that `ServiceInstance` is really a `VSGTenant`, then `leaf_model` will perform that conversion for you automatically.

### Removing links between Service Instances

Links are removed by deleting the `ServiceInstanceLink` object. For example,

    # delete all links between some_vsg_tenant and some_vrouter_tenant
    for link in ServiceInstanceLink.objects.filter(provider_service_instance_id=some_vsg_tenant.id, subscriber_service_instance_id=some_vrouter_instance.id):
        link.delete() 

### Creating ServiceInterfaces

`ServiceInterfaces` allow you to type the links between `ServiceInstances`. For example, if one `ServiceInstance` provides a `WAN` interface and another `ServiceInstance` uses a `LAN` interface, you can explicitly connect those two interfaces. These are currently created in Tosca. For example,

    in#lanside:
      type: tosca.nodes.InterfaceType
      properties:
         direction: in

    out#lanside:
      type: tosca.nodes.InterfaceType
      properties:
         direction: out

    volt_lanside:
      type: tosca.nodes.ServiceInterface
      requirements:
        - service:
            node: service#volt
            relationship: tosca.relationships.MemberOfService
        - interface:
            node: out#lanside
            relationship: tosca.relationships.IsType

    vsg_lanside:
      type: tosca.nodes.ServiceInterface
      requirements:
        - service:
            node: service#vsg
            relationship: tosca.relationships.MemberOfService
        - interface:
            node: in#lanside
            relationship: tosca.relationships.IsType

This example creates a `lanside` interface that is present in both the `VOLT` and `VSG` services. 

Interfaces are currently optional, but may become mandatory in the next release. Until then, you can optionally associate links with interfaces. For example,

    interface_type = InterfaceType.objects.get(name="lanside", direction="in")
    interface = VSGService.Interfaces.get(interface_type=interface_type)
    t = VSGTenant(owner=vsg_service)
    t.save()
    l = ServiceInstanceLink(provider_service_instance = t, 
                            provider_service_interface = interface,
                            subscriber_service_interface=some_volt_tenant)
    l.save()

As `ServiceInterface` are not mandatory, it's suggested that you perform the other migration steps, and leave `ServiceInterfaces` until everything else is working.