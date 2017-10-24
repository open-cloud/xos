
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


import unittest
import os
from xosgenx.generator import XOSGenerator
from helpers import FakeArgs
import yaml

PROTO_EXPECTED_OUTPUT = """
message VRouterPort {
  option bases = "XOSBase";
  optional string name = 1 [ null = "True",  max_length = "20",  blank = "True",  help_text = ""port friendly name"",  modifier = "optional",  db_index = "False" ];
  required string openflow_id = 2 [ null = "False",  max_length = "21",  blank = "False",  help_text = ""port identifier in ONOS"",  modifier = "required",  db_index = "False" ];
  required int32 vrouter_device = 3 [ null = "False",  blank = "False",  model = "VRouterDevice",  modifier = "required",  type = "link",  port = "ports",  link_type = "manytoone",  db_index = "True" ];
  required int32 vrouter_service = 4 [ null = "False",  blank = "False",  model = "VRouterService",  modifier = "required",  type = "link",  port = "device_ports",  link_type = "manytoone",  db_index = "True" ];
}
"""
VROUTER_XPROTO = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + "/xproto/vrouterport.xproto")

# Generate other formats from xproto
class XProtoTranslatorTest(unittest.TestCase):
    def _test_proto_generator(self):
        args = FakeArgs()
        args.files = [VROUTER_XPROTO]
        args.target = 'proto.xtarget'
        output = XOSGenerator.generate(args)
        self.assertEqual(output, PROTO_EXPECTED_OUTPUT)

    def test_yaml_generator(self):
        xproto = \
"""
option app_label = "test";

message Port (PlCoreBase,ParameterMixin){
     required manytoone network->Network:links = 1 [db_index = True, null = False, blank = False];
     optional manytoone instance->Instance:ports = 2 [db_index = True, null = True, blank = True];
     optional string ip = 3 [max_length = 39, content_type = "ip", blank = True, help_text = "Instance ip address", null = True, db_index = False];
     optional string port_id = 4 [help_text = "Neutron port id", max_length = 256, null = True, db_index = False, blank = True];
     optional string mac = 5 [help_text = "MAC address associated with this port", max_length = 256, null = True, db_index = False, blank = True];
     required bool xos_created = 6 [default = False, null = False, db_index = False, blank = True];
}

message Instance (PlCoreBase){
     optional string instance_id = 1 [max_length = 200, content_type = "stripped", blank = True, help_text = "Nova instance id", null = True, db_index = False];
     optional string instance_uuid = 2 [max_length = 200, content_type = "stripped", blank = True, help_text = "Nova instance uuid", null = True, db_index = False];
     required string name = 3 [max_length = 200, content_type = "stripped", blank = False, help_text = "Instance name", null = False, db_index = False];
     optional string instance_name = 4 [max_length = 200, content_type = "stripped", blank = True, help_text = "OpenStack generated name", null = True, db_index = False];
     optional string ip = 5 [max_length = 39, content_type = "ip", blank = True, help_text = "Instance ip address", null = True, db_index = False];
     required manytoone image->Image:instances = 6 [db_index = True, null = False, blank = False];
     optional manytoone creator->User:instances = 7 [db_index = True, null = True, blank = True];
     required manytoone slice->Slice:instances = 8 [db_index = True, null = False, blank = False];
     required manytoone deployment->Deployment:instance_deployment = 9 [db_index = True, null = False, blank = False];
     required manytoone node->Node:instances = 10 [db_index = True, null = False, blank = False];
     required int32 numberCores = 11 [help_text = "Number of cores for instance", default = 0, null = False, db_index = False, blank = False];
     required manytoone flavor->Flavor:instance = 12 [help_text = "Flavor of this instance", default = "get_default_flavor()", null = False, db_index = True, blank = False];
     optional string userData = 13 [help_text = "user_data passed to instance during creation", null = True, db_index = False, blank = True];
     required string isolation = 14 [default = "vm", choices = "(('vm', 'Virtual Machine'), ('container', 'Container'), ('container_vm', 'Container In VM'))", max_length = 30, blank = False, null = False, db_index = False];
     optional string volumes = 15 [help_text = "Comma-separated list of directories to expose to parent context", null = True, db_index = False, blank = True];
     optional manytoone parent->Instance:instance = 16 [help_text = "Parent Instance for containers nested inside of VMs", null = True, db_index = True, blank = True];
     required manytomany tags->Tag = 17 [db_index = False, null = False, blank = True];
}

message Network (PlCoreBase,ParameterMixin) {
     required string name = 1 [db_index = False, max_length = 32, null = False, blank = False];
     required manytoone template->NetworkTemplate:network = 2 [db_index = True, null = False, blank = False];
     required string subnet = 3 [db_index = False, max_length = 32, null = False, blank = True];
     required string start_ip = 4 [db_index = False, max_length = 32, null = False, blank = True];
     required string end_ip = 5 [db_index = False, max_length = 32, null = False, blank = True];
     optional string ports = 6 [db_index = False, max_length = 1024, null = True, blank = True];
     optional string labels = 7 [db_index = False, max_length = 1024, null = True, blank = True];
     required manytoone owner->Slice:ownedNetworks = 8 [help_text = "Slice that owns control of this Network", null = False, db_index = True, blank = False];
     required int32 guaranteed_bandwidth = 9 [default = 0, null = False, db_index = False, blank = False];
     required bool permit_all_slices = 10 [default = False, null = False, db_index = False, blank = True];
     optional string topology_parameters = 11 [db_index = False, null = True, blank = True];
     optional string controller_url = 12 [db_index = False, max_length = 1024, null = True, blank = True];
     optional string controller_parameters = 13 [db_index = False, null = True, blank = True];
     optional string network_id = 14 [help_text = "Quantum network", max_length = 256, null = True, db_index = False, blank = True];
     optional string router_id = 15 [help_text = "Quantum router id", max_length = 256, null = True, db_index = False, blank = True];
     optional string subnet_id = 16 [help_text = "Quantum subnet id", max_length = 256, null = True, db_index = False, blank = True];
     required bool autoconnect = 17 [help_text = "This network can be autoconnected to the slice that owns it", default = True, null = False, db_index = False, blank = True];
     required manytomany permitted_slices->Slice/Network_permitted_slices:availableNetworks = 18 [db_index = False, null = False, blank = True];
     required manytomany slices->Slice/NetworkSlice:networks = 19 [db_index = False, null = False, blank = True];
     required manytomany instances->Instance/Port:networks = 20 [db_index = False, null = False, blank = True];
}

message Slice (PlCoreBase){
     required string name = 1 [max_length = 80, content_type = "stripped", blank = False, help_text = "The Name of the Slice", null = False, db_index = False];
     required bool enabled = 2 [help_text = "Status for this Slice", default = True, null = False, db_index = False, blank = True];
     required bool omf_friendly = 3 [default = False, null = False, db_index = False, blank = True];
     required string description = 4 [help_text = "High level description of the slice and expected activities", max_length = 1024, null = False, db_index = False, blank = True];
     required string slice_url = 5 [db_index = False, max_length = 512, null = False, content_type = "url", blank = True];
     required manytoone site->Site:slices = 6 [help_text = "The Site this Slice belongs to", null = False, db_index = True, blank = False];
     required int32 max_instances = 7 [default = 10, null = False, db_index = False, blank = False];
     optional manytoone service->Service:slices = 8 [db_index = True, null = True, blank = True];
     optional string network = 9 [blank = True, max_length = 256, null = True, db_index = False, choices = "((None, 'Default'), ('host', 'Host'), ('bridged', 'Bridged'), ('noauto', 'No Automatic Networks'))"];
     optional string exposed_ports = 10 [db_index = False, max_length = 256, null = True, blank = True];
     optional manytoone serviceClass->ServiceClass:slices = 11 [db_index = True, null = True, blank = True];
     optional manytoone creator->User:slices = 12 [db_index = True, null = True, blank = True];
     optional manytoone default_flavor->Flavor:slices = 13 [db_index = True, null = True, blank = True];
     optional manytoone default_image->Image:slices = 14 [db_index = True, null = True, blank = True];
     optional manytoone default_node->Node:slices = 15 [db_index = True, null = True, blank = True];
     optional string mount_data_sets = 16 [default = "GenBank", max_length = 256, content_type = "stripped", blank = True, null = True, db_index = False];
     required string default_isolation = 17 [default = "vm", choices = "(('vm', 'Virtual Machine'), ('container', 'Container'), ('container_vm', 'Container In VM'))", max_length = 30, blank = False, null = False, db_index = False];
     required manytomany tags->Tag = 18 [db_index = False, null = False, blank = True];
}
"""

        args = FakeArgs()
        args.inputs = xproto
        args.target = 'modeldefs.xtarget'
        output = XOSGenerator.generate(args)

        yaml_ir = yaml.load(output)
        self.assertEqual(len(yaml_ir['items']), 4)

    def test_gui_hidden_models(self):
        xproto = \
"""
option app_label = "test";

message Foo {
    option gui_hidden = True;
    required string name = 1 [ null = "False", blank="False"];
}

message Bar {
    option gui_hidden = "False";
    required string name = 1 [ null = "False", blank="False"];
}
"""
        args = FakeArgs()
        args.inputs = xproto
        args.target = 'modeldefs.xtarget'
        output = XOSGenerator.generate(args)
        yaml_ir = yaml.load(output)
        self.assertEqual(len(yaml_ir['items']), 1)
        self.assertIn('Bar', output)
        self.assertNotIn('Foo', output)

    def test_gui_hidden_model_fields(self):
        xproto = \
"""
option app_label = "test";

message Foo {
    required string name = 1 [ null = "False", blank="False"];
    required string secret = 1 [ null = "False", blank="False", gui_hidden = "True"];
}
"""
        args = FakeArgs()
        args.inputs = xproto
        args.target = 'modeldefs.xtarget'
        output = XOSGenerator.generate(args)
        yaml_ir = yaml.load(output)
        self.assertEqual(len(yaml_ir['items']), 1)
        self.assertIn('name', output)
        self.assertNotIn('secret', output)

    def test_static_options(self):
        xproto = \
"""
option app_label = "test";

message Foo {
    required string name = 1 [ null = "False", blank="False"];
    required string isolation = 14 [default = "vm", choices = "(('vm', 'Virtual Machine'), ('container', 'Container'), ('container_vm', 'Container In VM'))", max_length = 30, blank = False, null = False, db_index = False];
}
"""

        args = FakeArgs()
        args.inputs = xproto
        args.target = 'modeldefs.xtarget'
        output = XOSGenerator.generate(args)
        self.assertIn("options:", output)
        self.assertIn(" {'id': 'container_vm', 'label': 'Container In VM'}", output)

    def test_not_static_options(self):
        xproto = \
"""
option app_label = "test";

message Foo {
    required string name = 1 [ null = "False", blank="False"];
}
"""

        args = FakeArgs()
        args.inputs = xproto
        args.target = 'modeldefs.xtarget'
        output = XOSGenerator.generate(args)
        self.assertNotIn("options:", output)

    def test_default_value_in_modeldef(self):
        xproto = \
"""
option app_label = "test";

message Foo {
    required string name = 1 [ null = "False", blank="False", default = "bar"];
    required string falsetrue = 1 [ null = "False", blank="False", default = False];
    required string truefalse = 1 [ null = "False", blank="False", default = True];
    required string some = 1 [ null = "False", blank="False", default = None];
    required string zero = 1 [ null = "False", blank="False", default = 0];
}
"""

        args = FakeArgs()
        args.inputs = xproto
        args.target = 'modeldefs.xtarget'
        output = XOSGenerator.generate(args)
        self.assertIn('default: "bar"', output)
        self.assertIn('default: "false"', output)
        self.assertIn('default: "true"', output)
        self.assertIn('default: "null"', output)
        self.assertIn('default: "0"', output)

    def test_not_default_value_in_modeldef(self):
        xproto = \
"""
option app_label = "test";

message Foo {
    required string name = 1 [ null = "False", blank="False"];
}
"""

        args = FakeArgs()
        args.inputs = xproto
        args.target = 'modeldefs.xtarget'
        output = XOSGenerator.generate(args)
        self.assertNotIn('default:', output)

    def test_one_to_many_in_modeldef(self):
        xproto = \
"""
option app_label = "test";

message ServiceDependency {
    required manytoone provider_service->Service:provided_dependencies = 1;
    required manytoone subscriber_service->Service:subscribed_dependencies = 2;
}

message Service {
    required string name = 1;
}
"""

        args = FakeArgs()
        args.inputs = xproto
        args.target = 'modeldefs.xtarget'
        output = XOSGenerator.generate(args)
        # Service deps model
        self.assertIn('{model: Service, type: manytoone, on_field: provider_service}', output)
        self.assertIn('{model: Service, type: manytoone, on_field: provider_service}', output)

        # Service model
        self.assertIn('{model: ServiceDependency, type: onetomany, on_field: provider_service}', output)
        self.assertIn('{model: ServiceDependency, type: onetomany, on_field: provider_service}', output)

    def test_model_description(self):
        xproto = \
"""
option app_label = "test";

message Foo {
    option description="This is the Foo model";
    required string name = 1 [ null = "False", blank="False"];
    required string isolation = 14 [default = "vm", choices = "(('vm', 'Virtual Machine'), ('container', 'Container'), ('container_vm', 'Container In VM'))", max_length = 30, blank = False, null = False, db_index = False];
}

message Bar {
    required string name = 1;
}
"""

        args = FakeArgs()
        args.inputs = xproto
        args.target = 'modeldefs.xtarget'
        output = XOSGenerator.generate(args)
        self.assertIn('description: "This is the Foo model"', output)

    def test_model_verbose_name(self):
        xproto = \
"""
option app_label = "test";

message Foo {
    option verbose_name="Verbose Foo Name";
    required string name = 1 [ null = "False", blank="False"];
    required string isolation = 14 [default = "vm", choices = "(('vm', 'Virtual Machine'), ('container', 'Container'), ('container_vm', 'Container In VM'))", max_length = 30, blank = False, null = False, db_index = False];
}

message Bar {
    required string name = 1;
}
"""

        args = FakeArgs()
        args.inputs = xproto
        args.target = 'modeldefs.xtarget'
        output = XOSGenerator.generate(args)
        self.assertIn('verbose_name: "Verbose Foo Name"', output)

if __name__ == '__main__':
    unittest.main()


