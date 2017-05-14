from xproto_test_base import *

class XProtoParseTests(XProtoTest):
    def test_global_options(self):
        xproto = \
"""
    option kind = "vsg";
    option verbose_name = "vSG Service";
"""
        self.generate(xproto = xproto, target = "{{ options }}")
        self.assertIn("vsg", self.get_output())
        self.assertIn("vSG Service", self.get_output())

    def test_basic_proto(self):
	# Picked up standard protobuf file from https://github.com/google/protobuf/blob/master/examples/addressbook.proto
        xproto = \
"""
// See README.txt for information and build instructions.
//
// Note: START and END tags are used in comments to define sections used in
// tutorials.  They are not part of the syntax for Protocol Buffers.
//
// To get an in-depth walkthrough of this file and the related examples, see:
// https://developers.google.com/protocol-buffers/docs/tutorials

// [START declaration]
package tutorial;
// [END declaration]

// [START java_declaration]
option java_package = "com.example.tutorial";
option java_outer_classname = "AddressBookProtos";
// [END java_declaration]

// [START csharp_declaration]
option csharp_namespace = "Google.Protobuf.Examples.AddressBook";
// [END csharp_declaration]

// [START messages]
message Person {
  required string name = 1;
  required int32 id = 2;  // Unique ID number for this person.
  optional string email = 3 [symphony = "da da da dum"];

  enum PhoneType {
    MOBILE = 0;
    HOME = 1;
    WORK = 2;
  }

  required  string number = 1;
  optional PhoneType type = 2;

  repeated PhoneNumber phones = 4;
}

// Our address book file is just one of these.
message AddressBook {
  repeated Person people = 1;
}
// [END messages]
"""
        self.generate(xproto = xproto, target = "{{ proto }}")
        self.assertIn("PhoneNumber", self.get_output())

    def test_link_extensions(self):
	xproto = \
"""
message links {
    required manytoone vrouter_service->VRouterService:device_ports = 4 [db_index = True, null = False, blank = False];
}
"""
        self.generate(xproto = xproto, target = "{{ proto.messages.0.links }}")
        self.assertIn("VRouterService", self.get_output())
	
	pass

    def test_through_extensions(self):
	xproto = \
"""
message links {
    required manytomany vrouter_service->VRouterService/ServiceProxy:device_ports = 4 [db_index = True, null = False, blank = False];
}
"""
        self.generate(xproto = xproto, target = "{{ proto.messages.0.links.0.through }}")
        self.assertIn("ServiceProxy", self.get_output())
	
	pass

    def test_message_options(self):
	xproto = \
"""
message link {
    option type = "e1000";
}
"""
        self.generate(xproto = xproto, target = "{{ proto.messages.0.options.type }}")
        self.assertIn("e1000", self.get_output())

	pass

    def test_message_base(self):
	xproto = \
"""
message base(Base) {
}
"""
        self.generate(xproto = xproto, target = "{{ proto.messages.0.bases }}")
        self.assertIn("Base", self.get_output())
	pass

if __name__ == '__main__':
    unittest.main()


