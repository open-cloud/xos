from xproto_test_base import *

# Generate Protobuf from Xproto and then parse the resulting Protobuf
class XProtoProtobufGeneratorTest(XProtoTest):
    def test_proto_generator(self):
        xproto = \
"""
message VRouterPort (XOSBase){
     optional string name = 1 [help_text = "port friendly name", max_length = 20, null = True, db_index = False, blank = True];
     required string openflow_id = 2 [help_text = "port identifier in ONOS", max_length = 21, null = False, db_index = False, blank = False];
     required manytoone vrouter_device->VRouterDevice:ports = 3 [db_index = True, null = False, blank = False];
     required manytoone vrouter_service->VRouterService:device_ports = 4 [db_index = True, null = False, blank = False];
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
{% if b!='XOSBase' and 'Mixin' not in b%}
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

        fields = filter(lambda s:'Field(' in s, self.get_output().splitlines())
        self.assertEqual(len(fields), 2)
        links = filter(lambda s:'Key(' in s, self.get_output().splitlines())
        self.assertEqual(len(links), 2)

if __name__ == '__main__':
    unittest.main()


