
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
from xosgenx.generator import XOSGenerator
from helpers import FakeArgs, XProtoTestHelpers

# Generate from xproto, then generate from equivalent proto
class XPureProtobufGenerator(unittest.TestCase):
    def test_pure_proto(self):
		xproto = \
"""
message VRouterPort (XOSBase){
     optional string name = 1 [help_text = "port friendly name", max_length = 20, null = True, db_index = False, blank = True];
     required string openflow_id = 2 [help_text = "port identifier in ONOS", max_length = 21, null = False, db_index = False, blank = False];
     required manytoone vrouter_device->VRouterDevice:ports = 3 [db_index = True, null = False, blank = False];
     required manytoone vrouter_service->VRouterService:device_ports = 4 [db_index = True, null = False, blank = False];
}
"""

		proto = \
"""
message VRouterPort {
  option bases = "XOSBase";
  optional string name = 1 [ null = "True",  max_length = "20",  blank = "True",  help_text = "port friendly name",  modifier = "optional",  db_index = "False" ];
  required string openflow_id = 2 [ null = "False",  max_length = "21",  blank = "False",  help_text = "port identifier in ONOS",  modifier = "required",  db_index = "False" ];
  required int32 vrouter_device = 3 [ null = "False",  blank = "False",  model = "VRouterDevice",  modifier = "required",  type = "link",  port = "ports",  db_index = "True", link = "manytoone"];
  required int32 vrouter_service = 4 [ null = "False",  blank = "False",  model = "VRouterService",  modifier = "required",  type = "link",  port = "device_ports",  db_index = "True", link = "manytoone"];
}
"""
		target = XProtoTestHelpers.write_tmp_target(
"""
from header import *
{% for m in proto.messages %}
{% if file_exists(xproto_base_name(m.name)|lower+'_header.py') -%}from {{xproto_base_name(m.name)|lower }}_header import *{% endif %}
{% if file_exists(xproto_base_name(m.name)|lower+'_top.py') -%}{{ include_file(xproto_base_name(m.name)|lower+'_top.py') }} {% endif %}

{%- for l in m.links %}

{% if l.peer.name != m.name %}
from core.models.{{ l.peer.name | lower }} import {{ l.peer.name }}
{% endif %}

{%- endfor %}
{% for b in m.bases %}
{% if b!='XOSBase' and 'Mixin' not in b%}
from core.models.{{b.name | lower}} import {{ b.name }}
{% endif %}
{% endfor %}


class {{ m.name }}{{ xproto_base_def(m, m.bases) }}:
  # Primitive Fields (Not Relations)
  {% for f in m.fields %}
  {%- if not f.link -%}
  {{ f.name }} = {{ xproto_django_type(f.type, f.options) }}( {{ xproto_django_options_str(f) }} )
  {% endif %}
  {%- endfor %}

  # Relations
  {% for l in m.links %}
  {{ l.src_port }} = {{ xproto_django_link_type(l) }}( {%- if l.peer.name==m.name -%}'self'{%- else -%}{{ l.peer.name }} {%- endif -%}, {{ xproto_django_link_options_str(l, l.dst_port ) }} )
  {%- endfor %}

  {% if file_exists(m.name|lower + '_model.py') -%}{{ include_file(m.name|lower + '_model.py') | indent(width=2)}}{%- endif %}
  pass

{% if file_exists(xproto_base_name(m.name)|lower+'_bottom.py') -%}{{ include_file(xproto_base_name(m.name)|lower+'_bottom.py') }}{% endif %}
{% endfor %}
""")

		args_xproto = FakeArgs()
		args_xproto.inputs = xproto
		args_xproto.target = target
		xproto_gen = XOSGenerator.generate(args_xproto)

		count1 = len(xproto_gen.split('\n'))

		args_proto = FakeArgs()
		args_proto.inputs = proto
		args_proto.target = target
		args_proto.rev = True
		proto_gen = XOSGenerator.generate(args_proto)
		count2 = len(proto_gen.split('\n'))

		self.assertEqual(count1, count2)

    def test_pure_policies(self):
		xproto = \
"""
policy my_policy < exists x:a=b >
"""

		proto = \
"""
option my_policy = "policy:< exists x:a=b >";
"""
		target = XProtoTestHelpers.write_tmp_target(
"""
{{ policies }}
""")

		args_xproto = FakeArgs()
		args_xproto.inputs = xproto
		args_xproto.target = target
		xproto_gen = XOSGenerator.generate(args_xproto)

		args_proto = FakeArgs()
		args_proto.inputs = proto
		args_proto.target = target
		args_proto.rev = True
		proto_gen = XOSGenerator.generate(args_proto)

		self.assertEqual(proto_gen, xproto_gen)

if __name__ == '__main__':
    unittest.main()


