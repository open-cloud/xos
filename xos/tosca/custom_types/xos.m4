tosca_definitions_version: tosca_simple_yaml_1_0

# Note: Tosca derived_from isn't working the way I think it should, it's not
#    inheriting from the parent template. Until we get that figured out, use
#    m4 macros do our inheritance

define(xos_base_props,
            no-delete:
                type: boolean
                default: false
                description: do not allow Tosca to delete this object
            no-create:
                type: boolean
                default: false
                description: do not allow Tosca to create this object)
define(xos_base_service_caps,
            scalable:
                type: tosca.capabilities.Scalable
            service:
                type: tosca.capabilities.xos.Service)
define(xos_base_service_props,
            kind:
                type: string
                default: generic
            view_url:
                type: string
                required: false
            icon_url:
                type: string
                required: false
            enabled:
                type: boolean
                default: true
            published:
                type: boolean
                default: true
            public_key:
                type: string
                required: false)

# end m4 macros
#
# compile this with "m4 custom_types/xos.m4 > custom_types/xos.yaml"

node_types:
    tosca.nodes.Service:
        derived_from: tosca.nodes.Root
        capabilities:
            xos_base_service_caps
        properties:
            xos_base_service_props

    tosca.nodes.VCPEService:
        derived_from: tosca.nodes.Root
        capabilities:
            xos_base_service_caps
        properties:
            xos_base_service_props
            backend_network_label:
                type: string
                required: false

    tosca.nodes.VBNGService:
        derived_from: tosca.nodes.Root
        capabilities:
            xos_base_service_caps
        properties:
            xos_base_service_props
            vbng_url:
                type: string
                required: false

    tosca.nodes.CDNService:
        derived_from: tosca.nodes.Root
        capabilities:
            xos_base_service_caps
        properties:
            xos_base_service_props

    tosca.nodes.User:
        derived_from: tosca.nodes.Root

        capabilities:
            user:
                type: tosca.capabilities.xos.User

        properties:
            password:
                type: string
                required: true
            firstname:
                type: string
                required: true
            lastname:
                type: string
                required: true
            phone:
                type: string
                required: false
            user_url:
                type: string
                required: false
            public_key:
                type: string
                required: false
            is_active:
                type: boolean
                default: true
            is_admin:
                type: boolean
                default: false
            login_page:
                type: string
                required: false

    tosca.nodes.NetworkTemplate:
        derived_from: tosca.nodes.Root

        capabilities:
            network_template:
                type: tosca.capabilities.xos.NetworkTemplate

        properties:
            visibility:
                type: string
                default: private
            translation:
                type: string
                default: none
            shared_network_name:
                type: string
                required: false
            shared_network_id:
                type: string
                required: false
            topology_kind:
                type: string
                default: BigSwitch
            controller_kind:
                type: string
                required: false

    tosca.nodes.network.Network.XOS:
          # Due to bug? in implementation, we have to copy everything from
          # tosca definitions tosca.nodes.network.Network here rather than
          # using derived_from.
          derived_from: tosca.nodes.Root
          description: >
            The TOSCA Network node represents a simple, logical network service.
          properties:
            ip_version:
              type: integer
              required: no
              default: 4
              constraints:
                - valid_values: [ 4, 6 ]
              description: >
                The IP version of the requested network. Valid values are 4 for ipv4
                or 6 for ipv6.
            cidr:
              type: string
              required: no
              description: >
                The cidr block of the requested network.
            start_ip:
              type: string
              required: no
              description: >
                 The IP address to be used as the start of a pool of addresses within
                 the full IP range derived from the cidr block.
            end_ip:
              type: string
              required: no
              description: >
                  The IP address to be used as the end of a pool of addresses within
                  the full IP range derived from the cidr block.
            gateway_ip:
              type: string
              required: no
              description: >
                 The gateway IP address.
            network_name:
              type: string
              required: no
              description: >
                 An identifier that represents an existing Network instance in the
                 underlying cloud infrastructure or can be used as the name of the
                 newly created network. If network_name is provided and no other
                 properties are provided (with exception of network_id), then an
                 existing network instance will be used. If network_name is provided
                 alongside with more properties then a new network with this name will
                 be created.
            network_id:
              type: string
              required: no
              description: >
                 An identifier that represents an existing Network instance in the
                 underlying cloud infrastructure. This property is mutually exclusive
                 with all other properties except network_name. This can be used alone
                 or together with network_name to identify an existing network.
            segmentation_id:
              type: string
              required: no
              description: >
                 A segmentation identifier in the underlying cloud infrastructure.
                 E.g. VLAN ID, GRE tunnel ID, etc..
            dhcp_enabled:
              type: boolean
              required: no
              default: true
              description: >
                Indicates should DHCP service be enabled on the network or not.
        # XOS-specific
            ports:
                type: string
                required: false
            labels:
                type: string
                required: false
            permit_all_slices:
                type: boolean
                # In the data model, this is defaulted to false. However, to
                # preserve Tosca semantics, we default it to true instead.
                default: true
          capabilities:
            link:
              type: tosca.capabilities.network.Linkable

#    tosca.nodes.XOSNetwork:
#        derived_from: tosca.nodes.Root
#
#        capabilities:
#            network:
#                type: tosca.capabilities.xos.Network
#
#        properties:
#            ports:
#                type: string
#                required: false
#            labels:
#                type: string
#                required: false
#            permit_all_slices:
#                type: boolean
#                default: false
#            permitted_slices:
#                type: string
#                required: false

    tosca.nodes.Deployment:
        derived_from: tosca.nodes.Root
        capabilities:
            deployment:
                type: tosca.capabilities.xos.Deployment

    tosca.nodes.Controller:
        derived_from: tosca.nodes.Root
        capabilities:
            controller:
                type: tosca.capabilities.xos.Controller
        properties:
            backend_type:
                type: string
                required: false
            version:
                type: string
                required: false
            auth_url:
                type: string
                required: false
            admin_user:
                type: string
                required: false
            admin_password:
                type: string
                required: false
            admin_tenant:
                type: string
                required: false
            domain:
                type: string
                required: false

    tosca.nodes.Site:
        derived_from: tosca.nodes.Root
        capabilities:
            site:
                type: tosca.capabilities.xos.Site
        properties:
             display_name:
                 type: string
                 required: false
                 description: name of the site
             site_url:
                 type: string
                 required: false
             enabled:
                 type: boolean
                 default: true
             hosts_nodes:
                 type: boolean
                 default: true
             hosts_users:
                 type: boolean
                 default: true
             is_public:
                 type: boolean
                 default: true
             # location, longitude, latitude

    tosca.nodes.Slice:
        derived_from: tosca.nodes.Root
        capability:
            slice:
                type: tosca.capabilities.xos.Slice

    tosca.relationships.MemberOfSlice:
        derived_from: tosca.relationships.Root
        valid_target_types: [ tosca.capabilities.xos.Slice ]

    tosca.relationships.MemberOfService:
        derived_from: tosca.relationships.Root
        valid_target_types: [ tosca.capabilities.xos.Service ]

    tosca.relationships.MemberOfSite:
        derived_from: tosca.relationships.Root
        valid_target_types: [ tosca.capabilities.xos.Site ]

    tosca.relationships.TenantOfService:
        derived_from: tosca.relationships.Root
        valid_target_types: [ tosca.capabilities.xos.Service ]

    tosca.relationships.ControllerDeployment:
        derived_from: tosca.relationships.Root
        valid_target_types: [ tosca.capabilities.xos.Deployment ]

    tosca.relationships SiteDeployment:
        derived_from: tosca.relationships.Root
        valid_target_types: [ tosca.capabilities.xos.Deployment ]

    tosca.relationships.UsesController:
        derived_from: tosca.relationships.Root
        valid_target_types: [ tosca.capabilities.xos.Controller ]

    tosca.relationships.ConnectsToNetwork:
        derived_from: tosca.relationships.Root
        valid_target_types: [ tosca.capabilities.xos.Network ]

    #    tosca.relationships.OwnsNetwork:
    #        derived_from: tosca.relationships.Root
    #        valid_target_types: [ tosca.capabilities.xos.Network ]

    tosca.relationships.UsesNetworkTemplate:
        derived_from: tosca.relationships.Root
        valid_target_types: [ tosca.capabilities.xos.NetworkTemplate ]

    tosca.relationships.AdminPrivilege:
        derived_from: tosca.relationships.Root
        valid_target_types: [ tosca.capabilities.xos.Slice, tosca.capabiltys.xos.Site ]

    tosca.relationships.AccessPrivilege:
        derived_from: tosca.relationships.Root
        valid_target_types: [ tosca.capabilities.xos.Slice, tosca.capabiltys.xos.Site ]

    tosca.relationships.PIPrivilege:
        derived_from: tosca.relationships.Root
        valid_target_types: [ tosca.capabiltys.xos.Site ]

    tosca.relationships.TechPrivilege:
        derived_from: tosca.relationships.Root
        valid_target_types: [ tosca.capabiltys.xos.Site ]

    tosca.capabilities.xos.Service:
        derived_from: tosca.capabilities.Root
        description: An XOS Service

    tosca.capabilities.xos.Deployment:
        derived_from: tosca.capabilities.Root
        description: An XOS Deployment

    tosca.capabilities.xos.Controller:
        derived_from: tosca.capabilities.Root
        description: An XOS Controller

    tosca.capabilities.xos.Site:
        derived_from: tosca.capabilities.Root
        description: An XOS Site

    tosca.capabilities.xos.Slice:
        derived_from: tosca.capabilities.Root
        description: An XOS Slice

    tosca.capabilities.xos.NetworkTemplate:
        derived_from: tosca.capabilities.Root
        description: An XOS network template

#    tosca.capabilities.xos.Network:
#        derived_from: tosca.capabilities.Root
#        description: An XOS network

    tosca.capabilities.xos.User:
        derived_from: tosca.capabilities.Root
        description: An XOS user
