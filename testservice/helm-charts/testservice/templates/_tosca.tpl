{{/* vim: set filetype=mustache: */}}
{{/*
Copyright 2018-present Open Networking Foundation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/}}
{{- define "testservice.serviceTosca" -}}
tosca_definitions_version: tosca_simple_yaml_1_0
description: Set up testservice service
imports:
  - custom_types/testserviceservice.yaml

topology_template:
  node_templates:
    service#testservice:
      type: tosca.nodes.TestserviceService
      properties:
        name: testservice
        kind: Testservice
{{- end -}}
