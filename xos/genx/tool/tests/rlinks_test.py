from xproto_test_base import *

class XProtoRlinkTests(XProtoTest):
    def test_proto_generator(self):
        xproto = \
"""
message VRouterPort (PlCoreBase){
     optional string name = 1 [help_text = "port friendly name", max_length = 20, null = True, db_index = False, blank = True];
     required string openflow_id = 2 [help_text = "port identifier in ONOS", max_length = 21, null = False, db_index = False, blank = False];
     required manytoone vrouter_device->VRouterDevice:ports = 3 [db_index = True, null = False, blank = False];
     required manytoone vrouter_service->VRouterService:device_ports = 4 [db_index = True, null = False, blank = False];
}

message VRouterService (Service) {
     optional string rest_hostname = 1 [db_index = False, max_length = 255, null = True, content_type = "stripped", blank = True];
     required int32 rest_port = 2 [default = 8181, null = False, db_index = False, blank = False];
     required string rest_user = 3 [default = "onos", max_length = 255, content_type = "stripped", blank = False, null = False, db_index = False];
     required string rest_pass = 4 [default = "rocks", max_length = 255, content_type = "stripped", blank = False, null = False, db_index = False];
}

message VRouterDevice (PlCoreBase){
     optional string name = 1 [help_text = "device friendly name", max_length = 20, null = True, db_index = False, blank = True];
     required string openflow_id = 2 [help_text = "device identifier in ONOS", max_length = 20, null = False, db_index = False, blank = False];
     required string config_key = 3 [default = "basic", max_length = 32, blank = False, help_text = "configuration key", null = False, db_index = False];
     required string driver = 4 [help_text = "driver type", max_length = 32, null = False, db_index = False, blank = False];
     required manytoone vrouter_service->VRouterService:devices = 5 [db_index = True, null = False, blank = False];
}
"""
	target = \
"""
{% for m in proto.messages %}
   {% for r in m.rlinks %}
       {{ r }}
   {% endfor %}
{% endfor %} 
"""

        self.generate(xproto = xproto, target = target)
        self.assertIn("'src_port': 'device_ports'", self.get_output())
        self.assertIn("'src_port': 'ports'", self.get_output())

if __name__ == '__main__':
    unittest.main()


