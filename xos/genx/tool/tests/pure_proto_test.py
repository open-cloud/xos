from xproto_test_base import *

# Generate from xproto, then generate from equivalent proto
class XPureProtobufGenerator(XProtoTest):
    def test_pure_proto(self):
        xproto = \
"""
message VRouterPort (PlCoreBase){
     optional string name = 1 [help_text = "port friendly name", max_length = 20, null = True, db_index = False, blank = True];
     required string openflow_id = 2 [help_text = "port identifier in ONOS", max_length = 21, null = False, db_index = False, blank = False];
     required manytoone vrouter_device->VRouterDevice:ports = 3 [db_index = True, null = False, blank = False];
     required manytoone vrouter_service->VRouterService:device_ports = 4 [db_index = True, null = False, blank = False];
}
"""

        proto = \
"""
message VRouterPort {
  option bases = "PlCoreBase";
  optional string name = 1 [ null = "True",  max_length = "20",  blank = "True",  help_text = "port friendly name",  modifier = "optional",  db_index = "False" ];
  required string openflow_id = 2 [ null = "False",  max_length = "21",  blank = "False",  help_text = "port identifier in ONOS",  modifier = "required",  db_index = "False" ];
  required int32 vrouter_device = 3 [ null = "False",  blank = "False",  model = "VRouterDevice",  modifier = "required",  type = "link",  port = "ports",  db_index = "True", link = "manytoone"];
  required int32 vrouter_service = 4 [ null = "False",  blank = "False",  model = "VRouterService",  modifier = "required",  type = "link",  port = "device_ports",  db_index = "True", link = "manytoone"];
}
"""
	target = \
"""
from header import *
{% for m in proto.messages %}
{% if file_exists(xproto_base_name(m.name)|lower+'_header.py') -%}from {{xproto_base_name(m.name)|lower }}_header import *{% endif %}
{% if file_exists(xproto_base_name(m.name)|lower+'_top.py') -%}{{ include_file(xproto_base_name(m.name)|lower+'_top.py') }} {% endif %}

{%- for l in m.links %}

{% if l.peer != m.name %}
from core.models.{{ l.peer | lower }} import {{ l.peer }}
{% endif %}

{%- endfor %}
{% for b in m.bases %}
{% if b!='PlCoreBase' and 'Mixin' not in b%}
from core.models.{{b | lower}} import {{ b }}
{% endif %}
{% endfor %}


class {{ m.name }}{{ xproto_base_def(m.bases) }}:
  # Primitive Fields (Not Relations)
  {% for f in m.fields %}
  {%- if not f.link -%}
  {{ f.name }} = {{ xproto_django_type(f.type, f.options) }}( {{ xproto_django_options_str(f) }} )
  {% endif %}
  {%- endfor %}

  # Relations
  {% for l in m.links %}
  {{ l.src_port }} = {{ xproto_django_link_type(l) }}( {%- if l.peer==m.name -%}'self'{%- else -%}{{ l.peer }} {%- endif -%}, {{ xproto_django_link_options_str(l, l.dst_port ) }} )
  {%- endfor %}

  {% if file_exists(m.name|lower + '_model.py') -%}{{ include_file(m.name|lower + '_model.py') | indent(width=2)}}{%- endif %}
  pass

{% if file_exists(xproto_base_name(m.name)|lower+'_bottom.py') -%}{{ include_file(xproto_base_name(m.name)|lower+'_bottom.py') }}{% endif %}
{% endfor %}
"""

        self.generate(xproto = xproto, target = target)
	xproto_gen = self.get_output()
	count1 = len(xproto_gen.split('\n'))

	self.generate(xproto = proto, target = target, rev = True)
	proto_gen = self.get_output()
	count2 = len(proto_gen.split('\n'))

	self.assertEqual(count1, count2)

if __name__ == '__main__':
    unittest.main()


