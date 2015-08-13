tosca_definitions_version: tosca_simple_yaml_1_0

# Note: Tosca derived_from isn't working the way I think it should, it's not
#    inheriting from the parent template. Until we get that figured out, use
#    m4 macros do our inheritance

node_types:
    tosca.nodes.ServiceProvider:
        derived_from: tosca.nodes.Root

        capabilities:
            user:
                type: tosca.capabilities.xos.ServiceProvider

    tosca.nodes.ContentProvider:
        derived_from: tosca.nodes.Root

        capabilities:
            user:
                type: tosca.capabilities.xos.ContentProvider

    tosca.nodes.OriginServer:
        derived_from: tosca.nodes.Root

        capabilities:
            user:
                type: tosca.capabilities.xos.OriginServer

    tosca.nodes.CDNPrefix:
        derived_from: tosca.nodes.Root

        capabilities:
            user:
                type: tosca.capabilities.xos.CDNPrefix

    tosca.relationships.MemberOfServiceProvider:
        derived_from: tosca.relationships.Root
        valid_target_types: [ tosca.capabilities.xos.ServiceProvider ]

    tosca.relationships.MemberOfContentProvider:
        derived_from: tosca.relationships.Root
        valid_target_types: [ tosca.capabilities.xos.ContentProvider ]

    tosca.relationships.DefaultOriginServer:
        derived_from: tosca.relationships.Root
        valid_target_types: [ tosca.capabilities.xos.OriginServer ]

    tosca.capabilities.xos.ServiceProvider:
        derived_from: tosca.capabilities.Root

    tosca.capabilities.xos.ContentProvider:
        derived_from: tosca.capabilities.Root

    tosca.capabilities.xos.CDNPrefix:
        derived_from: tosca.capabilities.Root

    tosca.capabilities.xos.OriginServer:
        derived_from: tosca.capabilities.Root


