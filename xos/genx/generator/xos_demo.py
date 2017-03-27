#!/usr/bin/python

import plyproto.parser as plyproto


test2 = """package tutorial;

message Person {
  required onetoone brother -> Person:email                                     = 1;
  required int32 id                                                             = 2;
  optional string email                                                         = 3;
}

"""

parser = plyproto.ProtobufAnalyzer()

print(parser.parse_string(test2))
