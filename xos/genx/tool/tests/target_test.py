from xproto_test_base import *

class XProtoTargetTests(XProtoTest):
    def test_file_methods(self):
        target = \
"""
  {%% if file_exists("%s") %%}
    {{ include_file("%s") }}
  {%% endif %%}
"""%(TEST_FILE, TEST_FILE)

        self.generate(target=target)
        self.assertIn(TEST_OUTPUT, self.get_output())

    def test_xproto_lib(self):
        target = \
"""
  {{ xproto_first_non_empty([None, None, None, None, None, None, "Eureka"]) }}
"""
        self.generate(target=target)
        self.assertIn("Eureka", self.get_output())

    def test_context(self):
        target = \
"""
  {{ context.what }}
"""
        self.generate(target=target, kv='what:what is what')
        self.assertIn("what is what", self.get_output())

if __name__ == '__main__':
    unittest.main()


