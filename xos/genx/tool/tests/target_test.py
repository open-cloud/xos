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

    def test_pluralize(self):
        proto = \
"""
  message TestPluralize {
      // The following field has an explicitly specified plural
      required int anecdote = 1 [plural = "data"];
      // The following fields have automatically computed plurals
      required int sheep = 2;
      required int radius = 2;
      required int slice = 2;
      required int network = 2;
      required int omf_friendly = 2;
  }
"""

        target = \
"""
{% for m in proto.messages.0.fields -%}
{{ xproto_pluralize(m) }},
{%- endfor %}
"""
        self.generate(xproto=proto, target=target)
        self.assertEqual("data,sheep,radii,slices,networks,omf_friendlies", self.get_output().lstrip().rstrip().rstrip(','))

if __name__ == '__main__':
    unittest.main()


