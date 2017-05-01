import exceptions
import shutil
import sys
import unittest

from twisted.internet import reactor
from xosapi import xos_grpc_client

exitStatus = -1

# TODO: See if there's a way to stub this out using a fake xos_grpc_client
# instead of the real one.

class TestORM(unittest.TestCase):
    def test_repr_name(self):
        s = xos_grpc_client.coreapi.Slice(name="foo")
        self.assertNotEqual(s, None)
        self.assertEqual(repr(s), "<Slice: foo>")

    def test_str_name(self):
        s = xos_grpc_client.coreapi.Slice(name="foo")
        self.assertNotEqual(s, None)
        self.assertEqual(str(s), "foo")

    def test_dumpstr_name(self):
        s = xos_grpc_client.coreapi.Slice(name="foo")
        self.assertNotEqual(s, None)
        self.assertEqual(s.dumpstr(), 'name: "foo"\n')

    def test_repr_noname(self):
        s = xos_grpc_client.coreapi.Slice()
        self.assertNotEqual(s, None)
        self.assertEqual(repr(s), "<Slice: id-0>")

    def test_str_noname(self):
        s = xos_grpc_client.coreapi.Slice()
        self.assertNotEqual(s, None)
        self.assertEqual(str(s), "Slice-0")

    def test_dumpstr_noname(self):
        s = xos_grpc_client.coreapi.Slice()
        self.assertNotEqual(s, None)
        self.assertEqual(s.dumpstr(), '')

def test_callback():
    try:
        unittest.main()
    except exceptions.SystemExit, e:
        global exitStatus
        exitStatus = e.code

xos_grpc_client.start_api_parseargs(test_callback)

sys.exit(exitStatus)
