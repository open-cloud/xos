from xproto_test_base import *

# Generate Protobuf from Xproto and then parse the resulting Protobuf
class XProtoProtobufGeneratorTest(XProtoTest):
    # This test is disabled because of a bug in Protobuf generation from xproto
    # Namely, options appear with repeated double quotes: foo=""bar"" 
    # TODO: Fix this bug, and re-enable this test

    def __disabled_test_proto_generator(self):
        xproto = \
"""
message VRouterPort (PlCoreBase){
     optional string name = 1 [help_text = "port friendly name", max_length = 20, null = True, db_index = False, blank = True];
     required string openflow_id = 2 [help_text = "port identifier in ONOS", max_length = 21, null = False, db_index = False, blank = False];
     required manytoone vrouter_device->VRouterDevice:ports = 3 [db_index = True, null = False, blank = False];
     required manytoone vrouter_service->VRouterService:device_ports = 4 [db_index = True, null = False, blank = False];
}
"""
	target = \
"""
{% for m in proto.messages %}
message {{ m.name }} {
  option bases = "{{ m.bases | join(",") }}";
  {%- for f in m.fields %}
  {{ f.modifier }} {{f.type}} {{f.name}} = {{ f.id }}{% if f.options %} [{% for k,v in f.options.iteritems() %} {{ k }} = "{{ v}}"{% if not loop.last %},{% endif %} {% endfor %}]{% endif %};
  {%- endfor %}
}
{% endfor %}
"""

        self.generate(xproto = xproto, target = target)
        self.generate(xproto = self.get_output(), target = "{{ proto }}")
	output = self.get_output()

if __name__ == '__main__':
    unittest.main()


