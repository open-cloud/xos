import exceptions
import shutil
import sys
import unittest

# Command-line argument of -R will cause this test to use a real grpc server
# rather than the fake stub.

if "-R" in sys.argv:
    USE_FAKE_STUB = False
    sys.argv.remove("-R")
else:
    USE_FAKE_STUB = True

class TestORM(unittest.TestCase):
    def make_coreapi(self):
        if USE_FAKE_STUB:
            stub = FakeStub()
            api = ORMStub(stub=stub, package_name = "xos", sym_db = FakeSymDb(), empty = FakeObj)
            return api
        else:
            return xos_grpc_client.coreapi

    def test_repr_name(self):
        orm = self.make_coreapi()
        s = orm.Slice(name="foo")
        self.assertNotEqual(s, None)
        self.assertEqual(repr(s), "<Slice: foo>")

    def test_str_name(self):
        orm = self.make_coreapi()
        s = orm.Slice(name="foo")
        self.assertNotEqual(s, None)
        self.assertEqual(str(s), "foo")

    def test_dumpstr_name(self):
        orm = self.make_coreapi()
        s = orm.Slice(name="foo")
        self.assertNotEqual(s, None)
        self.assertEqual(s.dumpstr(), 'name: "foo"\n')

    def test_repr_noname(self):
        orm = self.make_coreapi()
        s = orm.Slice()
        self.assertNotEqual(s, None)
        self.assertEqual(repr(s), "<Slice: id-0>")

    def test_str_noname(self):
        orm = self.make_coreapi()
        s = orm.Slice()
        self.assertNotEqual(s, None)
        self.assertEqual(str(s), "Slice-0")

    def test_dumpstr_noname(self):
        orm = self.make_coreapi()
        s = orm.Slice()
        self.assertNotEqual(s, None)
        self.assertEqual(s.dumpstr(), '')

if USE_FAKE_STUB:
    sys.path.append("..")

    from fake_stub import FakeStub, FakeSymDb, FakeObj
    from orm import ORMStub

    print "Using Fake Stub"

    unittest.main()
else:
    # This assumes xos-client python library is installed, and a gRPC server
    # is available.

    from twisted.internet import reactor
    from xosapi import xos_grpc_client

    print "Using xos-client library and core server"

    def test_callback():
        try:
            unittest.main()
        except exceptions.SystemExit, e:
            global exitStatus
            exitStatus = e.code

    xos_grpc_client.start_api_parseargs(test_callback)

    sys.exit(exitStatus)

