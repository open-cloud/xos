from xproto_test_base import *
from lib import FieldNotFound

class XProtoFieldGraphTest(XProtoTest):
    def test_field_graph(self):
        xproto = \
"""
message VRouterDevice (PlCoreBase){
     optional string name = 1 [help_text = "device friendly name", max_length = 20, null = True, db_index = False, blank = True, unique_with="openflow_id"];
     required string openflow_id = 2 [help_text = "device identifier in ONOS", max_length = 20, null = False, db_index = False, blank = False, unique_with="name"];
     required string config_key = 3 [default = "basic", max_length = 32, blank = False, help_text = "configuration key", null = False, db_index = False, unique_with="driver"];
     required string driver = 4 [help_text = "driver type", max_length = 32, null = False, db_index = False, blank = False, unique_with="vrouter_service"];
     required manytoone vrouter_service->VRouterService:devices = 5 [db_index = True, null = False, blank = False];
     required string A = 6 [unique_with="B"];
     required string B = 7 [unique_with="C"];
     required string C = 8 [unique_with="A"];
     required string D = 9;
     required string E = 10 [unique_with="F,G"];
     required string F = 11;
     required string G = 12;
}
"""
	target = \
"""
{{ xproto_field_graph_components(proto.messages.0.fields) }}
"""

        self.generate(xproto = xproto, target = target)
        components = eval(self.get_output())
        self.assertIn({'A','B','C'}, components)
        self.assertIn({'openflow_id','name'}, components)
        self.assertIn({'config_key','vrouter_service','driver'}, components)
        self.assertIn({'E','F','G'}, components)
        
        union = reduce(lambda acc,x: acc | x, components)
        self.assertNotIn('D', union) 

    def test_missing_field(self):
        xproto = \
"""
message VRouterDevice (PlCoreBase){
     optional string name = 1 [help_text = "device friendly name", max_length = 20, null = True, db_index = False, blank = True, unique_with="hamburger"];
     required string openflow_id = 2 [help_text = "device identifier in ONOS", max_length = 20, null = False, db_index = False, blank = False, unique_with="name"];
     required string config_key = 3 [default = "basic", max_length = 32, blank = False, help_text = "configuration key", null = False, db_index = False, unique_with="driver"];
     required string driver = 4 [help_text = "driver type", max_length = 32, null = False, db_index = False, blank = False, unique_with="vrouter_service"];
     required manytoone vrouter_service->VRouterService:devices = 5 [db_index = True, null = False, blank = False];
     required string A = 6 [unique_with="B"];
     required string B = 7 [unique_with="C"];
     required string C = 8 [unique_with="A"];
     required string D = 9;
}
"""
	target = \
"""
{{ xproto_field_graph_components(proto.messages.0.fields) }}
"""

        def generate():
            self.generate(xproto = xproto, target = target)

        # The following call generates some output, which should disappear
        # when Matteo merges his refactoring of XOSGenerator.
        self.assertRaises(FieldNotFound, generate)

if __name__ == '__main__':
    unittest.main()


