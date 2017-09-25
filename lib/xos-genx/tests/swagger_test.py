
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

import yaml
from xosgenx.generator import XOSGenerator
from helpers import FakeArgs, OUTPUT_DIR

class Args:
    pass

class XOSGeneratorTest(unittest.TestCase):

    def test_swagger_target(self):
        """
        [XOS-GenX] The swagger xtarget should generate the appropriate json
        """

        # xosgenx --output . --target xosgenx/targets/swagger.xtarget --write-to-file single  --dest-file swagger.yaml ../../xos/core/models/core.xproto
        # http-server --cors Users/teone/Sites/opencord/orchestration/xos/lib/xos-genx/
        xproto = \
            """
            option app_label = "core";
    
            message Instance::instance_policy (XOSBase) {
                 option validators = "instance_creator:Instance has no creator, instance_isolation: Container instance {obj.name} must use container image, instance_isolation_container_vm_parent:Container-vm instance {obj.name} must have a parent, instance_parent_isolation_container_vm:Parent field can only be set on Container-vm instances ({obj.name}), instance_isolation_vm: VM Instance {obj.name} must use VM image, instance_creator_privilege: instance creator has no privileges on slice";
                 optional string instance_id = 1 [max_length = 200, content_type = "stripped", blank = True, help_text = "Nova instance id", null = True, db_index = False];
                 optional string instance_uuid = 2 [max_length = 200, content_type = "stripped", blank = True, help_text = "Nova instance uuid", null = True, db_index = False];
                 required string name = 3 [max_length = 200, content_type = "stripped", blank = False, help_text = "Instance name", null = False, db_index = False];
                 optional string instance_name = 4 [max_length = 200, content_type = "stripped", blank = True, help_text = "OpenStack generated name", null = True, db_index = False];
                 optional string ip = 5 [max_length = 39, content_type = "ip", blank = True, help_text = "Instance ip address", null = True, db_index = False, gui_hidden = True];
                 required manytoone image->Image:instances = 6 [db_index = True, null = False, blank = False];
                 optional manytoone creator->User:instances = 7 [db_index = True, null = True, blank = True];
                 required manytoone slice->Slice:instances = 8 [db_index = True, null = False, blank = False];
                 required manytoone deployment->Deployment:instance_deployment = 9 [db_index = True, null = False, blank = False];
                 required manytoone node->Node:instances = 10 [db_index = True, null = False, blank = False];
                 required int32 numberCores = 11 [help_text = "Number of cores for instance", default = 0, null = False, db_index = False, blank = False];
                 required manytoone flavor->Flavor:instance = 12 [help_text = "Flavor of this instance", null = False, db_index = True, blank = False];
                 optional string userData = 13 [help_text = "user_data passed to instance during creation", null = True, db_index = False, blank = True, varchar = True];
                 required string isolation = 14 [default = "vm", choices = "(('vm', 'Virtual Machine'), ('container', 'Container'), ('container_vm', 'Container In VM'))", max_length = 30, blank = False, null = False, db_index = False];
                 optional string volumes = 15 [help_text = "Comma-separated list of directories to expose to parent context", null = True, db_index = False, blank = True];
                 optional manytoone parent->Instance:instance = 16 [help_text = "Parent Instance for containers nested inside of VMs", null = True, db_index = True, blank = True];
            }
            """
        args = FakeArgs()
        args.inputs = xproto
        args.target = 'swagger.xtarget'
        args.output = OUTPUT_DIR
        args.write_to_file = "single"
        args.dest_file = "swagger.yaml"
        args.quiet = False
        output = XOSGenerator.generate(args)
        self.assertIn("/xosapi/v1/core/instances/:", output)
        self.assertIn("/xosapi/v1/core/instances/{id}:", output)
        self.assertIn("Instance:", output)

if __name__ == '__main__':
    unittest.main()
