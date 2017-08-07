
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

    tosca.nodes.HpcHealthCheck:
        derived_from: tosca.nodes.Root

        properties:
            kind:
                type: string
                required: true
                description: dns | http | nameserver
            resource_name:
                type: string
                required: true
                description: name of resource to query
            result_contains:
                type: string
                required: false
                description: soemthing to look for inside the result
        capabilities:
            healthcheck:
                type: tosca.capabilities.xos.HpcHealthCheck

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

    tosca.capabilities.xos.HpcHealthCheck:
        derived_from: tosca.capabilities.Root


