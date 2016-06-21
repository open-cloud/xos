# Note: Tosca derived_from isn't working the way I think it should, it's not
#    inheriting from the parent template. Until we get that figured out, use
#    m4 macros do our inheritance

define(xos_base_props,
            no-delete:
                type: boolean
                default: false
                description: Do not allow Tosca to delete this object
            no-create:
                type: boolean
                default: false
                description: Do not allow Tosca to create this object
            no-update:
                type: boolean
                default: false
                description: Do not allow Tosca to update this object
            replaces:
                type: string
                required: false
                descrption: Replaces/renames this object)
# Service
define(xos_base_service_caps,
            scalable:
                type: tosca.capabilities.Scalable
            service:
                type: tosca.capabilities.xos.Service)
define(xos_base_service_props,
            kind:
                type: string
                default: generic
                description: Type of service.
            view_url:
                type: string
                required: false
                description: URL to follow when icon is clicked in the Service Directory.
            icon_url:
                type: string
                required: false
                description: ICON to display in the Service Directory.
            enabled:
                type: boolean
                default: true
            published:
                type: boolean
                default: true
                description: If True then display this Service in the Service Directory.
            public_key:
                type: string
                required: false
                description: Public key to install into Instances to allows Services to SSH into them.
            private_key_fn:
                type: string
                required: false
                description: Location of private key file
            versionNumber:
                type: string
                required: false
                description: Version number of Service.)
# Subscriber
define(xos_base_subscriber_caps,
            subscriber:
                type: tosca.capabilities.xos.Subscriber)
define(xos_base_subscriber_props,
            kind:
                type: string
                default: generic
                description: Kind of subscriber
            service_specific_id:
                type: string
                required: false
                description: Service specific ID opaque to XOS but meaningful to service)
define(xos_base_tenant_props,
            kind:
                type: string
                default: generic
                description: Kind of tenant
            service_specific_id:
                type: string
                required: false
                description: Service specific ID opaque to XOS but meaningful to service)

# end m4 macros

