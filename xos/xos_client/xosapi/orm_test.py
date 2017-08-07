
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
            api = xosapi.orm.ORMStub(stub=stub, package_name = "xos", sym_db = FakeSymDb(), empty = FakeObj, enable_backoff = False)
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

    def test_create(self):
        orm = self.make_coreapi()
        site = orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)

    def test_get(self):
        orm = self.make_coreapi()
        site = orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)
        got_site = orm.Site.objects.get(id = site.id)
        self.assertNotEqual(got_site, None)
        self.assertEqual(got_site.id, site.id)

    def test_delete(self):
        orm = self.make_coreapi()
        orig_len_sites = len(orm.Site.objects.all())
        site = orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)
        site.delete()
        sites = orm.Site.objects.all()
        self.assertEqual(len(sites), orig_len_sites)

    def test_objects_all(self):
        orm = self.make_coreapi()
        orig_len_sites = len(orm.Site.objects.all())
        site = orm.Site(name="mysite")
        site.save()
        sites = orm.Site.objects.all()
        self.assertEqual(len(sites), orig_len_sites+1)

    def test_objects_first(self):
        orm = self.make_coreapi()
        site = orm.Site(name="mysite")
        site.save()
        site = orm.Site.objects.first()
        self.assertNotEqual(site, None)

    def test_content_type_map(self):
        orm = self.make_coreapi()
        self.assertTrue( "Slice" in orm.content_type_map.values() )
        self.assertTrue( "Site" in orm.content_type_map.values() )
        self.assertTrue( "Tag" in orm.content_type_map.values() )

    def test_foreign_key_get(self):
        orm = self.make_coreapi()
        site = orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)
        slice = orm.Slice(name="mysite_foo", site_id = site.id)
        slice.save()
        self.assertTrue(slice.id > 0)
        self.assertNotEqual(slice.site, None)
        self.assertEqual(slice.site.id, site.id)

    def test_foreign_key_set(self):
        orm = self.make_coreapi()
        site = orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)
        slice = orm.Slice(name="mysite_foo", site = site)
        slice.save()
        slice.invalidate_cache()
        self.assertTrue(slice.id > 0)
        self.assertNotEqual(slice.site, None)
        self.assertEqual(slice.site.id, site.id)

    def test_foreign_key_create_null(self):
        orm = self.make_coreapi()
        site = orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)
        slice = orm.Slice(name="mysite_foo", site = site, service=None)
        slice.save()
        slice.invalidate_cache()
        self.assertTrue(slice.id > 0)
        self.assertEqual(slice.service, None)

    def test_foreign_key_set_null(self):
        orm = self.make_coreapi()
        site = orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)
        service = orm.Service(name="myservice")
        service.save()
        self.assertTrue(service.id > 0)
        # start out slice.service is non-None
        slice = orm.Slice(name="mysite_foo", site = site, service=service)
        slice.save()
        slice.invalidate_cache()
        self.assertTrue(slice.id > 0)
        self.assertNotEqual(slice.service, None)
        self.assertEqual(slice.service.id, service.id)
        # now set it to None
        slice.service = None
        slice.save()
        slice.invalidate_cache()
        self.assertEqual(slice.service, None)


    def test_generic_foreign_key_get(self):
        orm = self.make_coreapi()
        service = orm.Service(name="myservice")
        service.save()
        site = orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)
        tag = orm.Tag(service=service, name="mytag", value="somevalue", content_type=site.self_content_type_id, object_id=site.id)
        tag.save()
        self.assertTrue(tag.id > 0)
        self.assertNotEqual(tag.content_object, None)
        self.assertEqual(tag.content_object.id, site.id)

    def test_generic_foreign_key_set(self):
        orm = self.make_coreapi()
        service = orm.Service(name="myservice")
        service.save()
        site = orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)
        tag = orm.Tag(service=service, name="mytag", value="somevalue")
        tag.content_object = site
        tag.invalidate_cache()
        self.assertEqual(tag.content_type, site.self_content_type_id)
        self.assertEqual(tag.object_id, site.id)
        tag.save()
        self.assertTrue(tag.id > 0)
        self.assertNotEqual(tag.content_object, None)
        self.assertEqual(tag.content_object.id, site.id)

if USE_FAKE_STUB:
    sys.path.append("..")

    import xosapi.orm
    from fake_stub import FakeStub, FakeSymDb, FakeObj

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
            sys.argv = sys.argv[:1] # unittest does not like xos_grpc_client's command line arguments (TODO: find a cooperative approach)
            unittest.main()
        except exceptions.SystemExit, e:
            global exitStatus
            exitStatus = e.code

    xos_grpc_client.start_api_parseargs(test_callback)

    sys.exit(exitStatus)

