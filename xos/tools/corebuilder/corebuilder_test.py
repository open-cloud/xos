
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


import shutil
import unittest
from corebuilder import *

class TestCoreBuilder(unittest.TestCase):
    def setUp(self):
        if not os.path.exists("/tmp/fake_library"):
            os.mkdir("/tmp/fake_library")
        file("/tmp/fake_library/fake.js","w").write("stuff")

    def tearDown(self):
        if os.path.exists("/tmp/fake_library"):
           shutil.rmtree("/tmp/fake_library")
        if os.path.exists("/opt/xos_corebuilder/BUILD/opt"):
           shutil.rmtree("/opt/xos_corebuilder/BUILD/opt")
        if os.path.exists("/tmp/recipe"):
           os.remove("/tmp/recipe")

    #--------------------------------------------------------------------------
    # test_XOSCoreBuilder_init
    #--------------------------------------------------------------------------

    def test_XOSCoreBuilder_init(self):
        recipe = \
"""tosca_definitions_version: tosca_simple_yaml_1_0

description: Onboard fake library

imports:
   - custom_types/xos.yaml

topology_template:
  node_templates:
    library#fake:
      type: tosca.nodes.Library
      properties:
          base_url: file:///tmp/fake_library/
          vendor_js: fake.js
"""
        file("/tmp/recipe", "w").write(recipe)

        CoreBuilderMissingResourceException(XOSCoreBuilder, ["/tmp/recipe"])

    #--------------------------------------------------------------------------
    # test_bad_recipe_name
    #--------------------------------------------------------------------------

    def test_bad_recipe_name(self):
        self.assertRaises(CoreBuilderMissingRecipeException,
                          XOSCoreBuilder,
                          ["/tmp/does_not_exit"])

    #--------------------------------------------------------------------------
    # test_missing_resource
    #--------------------------------------------------------------------------

    def test_missing_resource(self):
        recipe = \
"""tosca_definitions_version: tosca_simple_yaml_1_0

description: Onboard fake library

imports:
   - custom_types/xos.yaml

topology_template:
  node_templates:
    library#fake:
      type: tosca.nodes.Library
      properties:
          base_url: file:///tmp/fake_library/
          vendor_js: missing_fake.js
"""
        file("/tmp/recipe", "w").write(recipe)
        self.assertRaises(CoreBuilderMissingResourceException,
                          XOSCoreBuilder,
                          ["/tmp/recipe"])

    #--------------------------------------------------------------------------
    # test_malformed_url
    #--------------------------------------------------------------------------

    def test_malformed_url(self):
        recipe = \
"""tosca_definitions_version: tosca_simple_yaml_1_0

description: Onboard fake library

imports:
   - custom_types/xos.yaml

topology_template:
  node_templates:
    library#fake:
      type: tosca.nodes.Library
      properties:
          base_url: http:///tmp/fake_library/
          vendor_js: fake.js
"""
        file("/tmp/recipe", "w").write(recipe)
        self.assertRaises(CoreBuilderMalformedUrlException,
                          XOSCoreBuilder,
                          ["/tmp/recipe"])

    #--------------------------------------------------------------------------
    # test_malformed_value
    #--------------------------------------------------------------------------

    def test_malformed_value(self):
        recipe = \
"""tosca_definitions_version: tosca_simple_yaml_1_0

description: Onboard fake library

imports:
   - custom_types/xos.yaml

topology_template:
  node_templates:
    library#fake:
      type: tosca.nodes.Library
      properties:
          base_url: file:///tmp/fake_library/
          vendor_js: badvalue=bad fake.js
"""
        file("/tmp/recipe", "w").write(recipe)
        self.assertRaises(CoreBuilderMalformedValueException,
                          XOSCoreBuilder,
                          ["/tmp/recipe"])

    #--------------------------------------------------------------------------
    # test_unknown_resource
    #--------------------------------------------------------------------------

    def test_unknown_resource(self):
        recipe = \
"""tosca_definitions_version: tosca_simple_yaml_1_0

description: Onboard fake library

imports:
   - custom_types/xos.yaml

topology_template:
  node_templates:
    library#fake:
      type: tosca.nodes.Slice
"""
        file("/tmp/recipe", "w").write(recipe)
        self.assertRaises(CoreBuilderUnknownResourceException,
                          XOSCoreBuilder,
                          ["/tmp/recipe"])

if __name__ == '__main__':
    unittest.main()


