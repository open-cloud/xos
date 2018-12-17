
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
import os
import random
import shutil
import string
import sys
import unittest
from mock import patch

# by default, use fake stub rather than real core
USE_FAKE_STUB=True

PARENT_DIR=os.path.join(os.path.dirname(__file__), "..")

class TestORM(unittest.TestCase):
    def setUp(self):
        from xosconfig import Config
        test_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
        config = os.path.join(test_path, "test_config.yaml")
        Config.clear()
        Config.init(config, 'synchronizer-config-schema.yaml')
        if (USE_FAKE_STUB):
            sys.path.append(PARENT_DIR)

    def tearDown(self):
        if (USE_FAKE_STUB):
            sys.path.remove(PARENT_DIR)

    def make_coreapi(self):
        if USE_FAKE_STUB:
            import xosapi.orm
            from fake_stub import FakeStub, FakeProtos, FakeObj

            xosapi.orm.import_convenience_methods()

            stub = FakeStub()
            api = xosapi.orm.ORMStub(stub=stub, package_name = "xos", protos=FakeProtos(), empty = FakeObj, enable_backoff = False)
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
        user = orm.User(email="fake_" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)), site_id=site.id)
        user.save()
        self.assertTrue(user.id > 0)
        slice = orm.Slice(name="mysite_foo", site_id = site.id, creator_id = user.id)
        slice.save()
        self.assertTrue(slice.id > 0)
        self.assertNotEqual(slice.site, None)
        self.assertEqual(slice.site.id, site.id)

    def test_foreign_key_set_with_invalidate(self):
        orm = self.make_coreapi()
        site = orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)
        user = orm.User(email="fake_" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)), site_id=site.id)
        user.save()
        self.assertTrue(user.id > 0)
        slice = orm.Slice(name="mysite_foo", site = site, creator_id=user.id)
        slice.save()
        slice.invalidate_cache()
        self.assertTrue(slice.id > 0)
        self.assertNotEqual(slice.site, None)
        self.assertEqual(slice.site.id, site.id)
        if not USE_FAKE_STUB:
            self.assertTrue(slice.id in slice.site.slices_ids)

    def test_foreign_key_set_without_invalidate(self):
        orm = self.make_coreapi()
        site = orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)
        user = orm.User(email="fake_" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)), site_id=site.id)
        user.save()
        self.assertTrue(user.id > 0)
        slice = orm.Slice(name="mysite_foo", site = site, creator_id=user.id)
        slice.save()
        self.assertTrue(slice.id > 0)
        self.assertNotEqual(slice.site, None)
        self.assertEqual(slice.site.id, site.id)
        if not USE_FAKE_STUB:
            self.assertTrue(slice.id in slice.site.slices_ids)
            ids_from_models = [x.id for x in slice.site.slices.all()]
            self.assertTrue(slice.id in ids_from_models)

    def test_foreign_key_reset(self):
        orm = self.make_coreapi()
        site = orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)
        user = orm.User(email="fake_" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)), site_id=site.id)
        user.save()
        self.assertTrue(user.id > 0)
        slice = orm.Slice(name="mysite_foo", site = site, creator_id=user.id)
        slice.save()
        self.assertTrue(slice.id > 0)
        self.assertNotEqual(slice.site, None)
        self.assertEqual(slice.site.id, site.id)
        if not USE_FAKE_STUB:
            self.assertTrue(slice.id in site.slices_ids)
            self.assertTrue(slice.id in slice.site.slices_ids)

        site2 = orm.Site(name="mysite2")
        site2.save()
        slice.name = "mysite2_foo"
        slice.site = site2
        slice.save()
        self.assertNotEqual(slice.site, None)
        self.assertEqual(slice.site.id, site2.id)
        if not USE_FAKE_STUB:
            self.assertTrue(slice.id not in site.slices_ids)
            self.assertTrue(slice.id in site2.slices_ids)
            self.assertTrue(slice.id in slice.site.slices_ids)
            ids_from_models1 = [x.id for x in site.slices.all()]
            self.assertTrue(slice.id not in ids_from_models1)
            ids_from_models2 = [x.id for x in site2.slices.all()]
            self.assertTrue(slice.id in ids_from_models2)

    def test_foreign_key_back_and_forth_even(self):
        orm = self.make_coreapi()
        site = orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)
        user = orm.User(email="fake_" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)), site_id=site.id)
        user.save()
        self.assertTrue(user.id > 0)
        slice = orm.Slice(name="mysite_foo", site = site, creator_id=user.id)
        slice.save()
        self.assertTrue(slice.id > 0)
        self.assertNotEqual(slice.site, None)
        self.assertEqual(slice.site.id, site.id)
        if not USE_FAKE_STUB:
            self.assertTrue(slice.id in site.slices_ids)
            self.assertTrue(slice.id in slice.site.slices_ids)

        site2 = orm.Site(name="mysite2")
        site2.save()
        slice.name = "mysite2_foo"
        slice.site = site2
        slice.site = site
        slice.site = site2
        slice.site = site
        slice.save()
        self.assertNotEqual(slice.site, None)
        self.assertEqual(slice.site.id, site.id)
        if not USE_FAKE_STUB:
            self.assertTrue(slice.id not in site2.slices_ids)
            self.assertTrue(slice.id in site.slices_ids)
            self.assertTrue(slice.id in slice.site.slices_ids)

    def test_foreign_key_back_and_forth_odd(self):
        orm = self.make_coreapi()
        site = orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)
        user = orm.User(email="fake_" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)), site_id=site.id)
        user.save()
        self.assertTrue(user.id > 0)
        slice = orm.Slice(name="mysite_foo", site = site, creator_id=user.id)
        slice.save()
        self.assertTrue(slice.id > 0)
        self.assertNotEqual(slice.site, None)
        self.assertEqual(slice.site.id, site.id)
        if not USE_FAKE_STUB:
            self.assertTrue(slice.id in site.slices_ids)
            self.assertTrue(slice.id in slice.site.slices_ids)

        site2 = orm.Site(name="mysite2")
        site2.save()
        slice.name = "mysite2_foo"
        slice.site = site2
        slice.site = site
        slice.site = site2
        slice.site = site
        slice.site = site2
        slice.save()
        self.assertNotEqual(slice.site, None)
        self.assertEqual(slice.site.id, site2.id)
        if not USE_FAKE_STUB:
            self.assertTrue(slice.id not in site.slices_ids)
            self.assertTrue(slice.id in site2.slices_ids)
            self.assertTrue(slice.id in slice.site.slices_ids)

    def test_foreign_key_create_null(self):
        orm = self.make_coreapi()
        site = orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)
        user = orm.User(email="fake_" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)), site_id=site.id)
        user.save()
        self.assertTrue(user.id > 0)
        slice = orm.Slice(name="mysite_foo", site = site, service=None, creator_id=user.id)
        slice.save()
        slice.invalidate_cache()
        self.assertTrue(slice.id > 0)
        self.assertEqual(slice.service, None)

    def test_foreign_key_set_null(self):
        orm = self.make_coreapi()
        site = orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)
        user = orm.User(email="fake_" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10)), site_id=site.id)
        user.save()
        self.assertTrue(user.id > 0)
        service = orm.Service(name="myservice")
        service.save()
        self.assertTrue(service.id > 0)
        # start out slice.service is non-None
        slice = orm.Slice(name="mysite_foo", site = site, service=service, creator_id=user.id)
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

    def test_generic_foreign_key_get_decl(self):
        orm = self.make_coreapi()
        service = orm.Service(name="myservice")
        service.save()
        site = orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)
        tag = orm.Tag(service=service, name="mytag", value="somevalue", content_type=site.self_content_type_id + "_decl", object_id=site.id)
        tag.save()
        self.assertTrue(tag.id > 0)
        self.assertNotEqual(tag.content_object, None)
        self.assertEqual(tag.content_object.id, site.id)

    def test_generic_foreign_key_get_bad_contenttype(self):
        orm = self.make_coreapi()
        service = orm.Service(name="myservice")
        service.save()
        site = orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)
        tag = orm.Tag(service=service, name="mytag", value="somevalue", content_type="does_not_exist", object_id=site.id)
        tag.save()
        self.assertTrue(tag.id > 0)
        with self.assertRaises(Exception) as e:
            obj = tag.content_object
        self.assertEqual(e.exception.message, "Content_type does_not_exist not found in self.content_type_map")

    def test_generic_foreign_key_get_bad_id(self):
        orm = self.make_coreapi()
        service = orm.Service(name="myservice")
        service.save()
        site = orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)
        tag = orm.Tag(service=service, name="mytag", value="somevalue", content_type=site.self_content_type_id, object_id=4567)
        tag.save()
        self.assertTrue(tag.id > 0)
        with self.assertRaises(Exception) as e:
            obj = tag.content_object
        self.assertEqual(e.exception.message, "Object 4567 of model Site was not found")

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

    def test_leaf_model_trivial(self):
        orm = self.make_coreapi()
        service = orm.Service(name="myservice")
        service.save()
        self.assertEqual(service.leaf_model_name, "Service")

    def test_leaf_model_descendant(self):
        orm = self.make_coreapi()
        onos_service = orm.ONOSService(name="myservice")
        onos_service.save()
        self.assertEqual(onos_service.model_name, "ONOSService")
        self.assertEqual(onos_service.leaf_model_name, "ONOSService")

        service = orm.Service.objects.get(id=onos_service.id)
        self.assertEqual(service.id, onos_service.id)
        self.assertEqual(service.model_name, "Service")
        self.assertEqual(service.leaf_model_name, "ONOSService")

        onos_service_cast = service.leaf_model
        self.assertEqual(onos_service_cast.model_name, "ONOSService")
        self.assertEqual(onos_service_cast.leaf_model_name, "ONOSService")
        self.assertEqual(onos_service_cast.id, onos_service.id)

    def test_field_null(self):
        """ In a saved object, if a nullable field is left set to None, make sure the ORM returns None """

        orm = self.make_coreapi()
        tm = orm.TestModel()
        tm.save()

        tm = orm.TestModel.objects.all()[0]
        self.assertFalse(tm._wrapped_class.HasField("intfield"))
        self.assertEqual(tm.intfield, None)

    def test_field_null_new(self):
        """ For models that haven't been saved yet, reading the field should return the gRPC default """

        orm = self.make_coreapi()
        tm = orm.TestModel()

        self.assertEqual(tm.intfield, 0)

    def test_field_non_null(self):
        """ In a saved object, if a nullable field is set to a value, then make sure the ORM returns the value """

        orm = self.make_coreapi()
        tm = orm.TestModel(intfield=3)
        tm.save()

        tm = orm.TestModel.objects.all()[0]
        self.assertEqual(tm.intfield, 3)

    def test_field_set_null(self):
        """ Setting a field to None is not allowed """

        orm = self.make_coreapi()
        tm = orm.TestModel()
        with self.assertRaises(Exception) as e:
            tm.intfile = None
        self.assertEqual(e.exception.message, "Setting a non-foreignkey field to None is not supported")

    def test_query_iexact(self):
        orm = self.make_coreapi()
        with patch.object(orm.grpc_stub, "FilterTestModel", autospec=True) as filter:
            orm.TestModel.objects.filter(name__iexact = "foo")
            self.assertEqual(filter.call_count, 1)
            q = filter.call_args[0][0]

            self.assertEqual(q.kind, q.DEFAULT)
            self.assertEqual(len(q.elements), 1)
            self.assertEqual(q.elements[0].operator, q.elements[0].IEXACT)
            self.assertEqual(q.elements[0].sValue, "foo")

    def test_query_equal(self):
        orm = self.make_coreapi()
        with patch.object(orm.grpc_stub, "FilterTestModel", autospec=True) as filter:
            orm.TestModel.objects.filter(name = "foo")
            self.assertEqual(filter.call_count, 1)
            q = filter.call_args[0][0]

            self.assertEqual(q.kind, q.DEFAULT)
            self.assertEqual(len(q.elements), 1)
            self.assertEqual(q.elements[0].operator, q.elements[0].EQUAL)
            self.assertEqual(q.elements[0].sValue, "foo")

    def test_ORMWrapper_new_diff(self):
        orm = self.make_coreapi()
        site = orm.Site(name="mysite")

        self.assertEqual(site.is_new, True)
        self.assertEqual(site._dict, {"name": "mysite"})
        self.assertEqual(site.diff, {})
        self.assertEqual(site.changed_fields, ["name"])
        self.assertEqual(site.has_field_changed("name"), False)
        self.assertEqual(site.has_field_changed("login_base"), False)

        site.login_base = "bar"

        self.assertEqual(site._dict, {'login_base': 'bar', 'name': 'mysite'})
        self.assertEqual(site.diff, {'login_base': (None, 'bar')})
        self.assertIn("name", site.changed_fields)
        self.assertIn("login_base", site.changed_fields)
        self.assertEqual(site.has_field_changed("name"), False)
        self.assertEqual(site.has_field_changed("login_base"), True)
        self.assertEqual(site.get_field_diff("login_base"), (None, "bar"))

    def test_ORMWrapper_existing_diff(self):
        orm = self.make_coreapi()
        site = orm.Site(name="mysite", login_base="foo")
        site.save()
        site = orm.Site.objects.first()

        self.assertEqual(site.is_new, False)
        self.assertEqual(site._dict, {"id": 1, "name": "mysite", "login_base": "foo"})
        self.assertEqual(site.diff, {})
        self.assertEqual(site.changed_fields, [])
        self.assertEqual(site.has_field_changed("name"), False)
        self.assertEqual(site.has_field_changed("login_base"), False)

        site.login_base = "bar"

        self.assertEqual(site._dict, {'id': 1, 'login_base': 'bar', 'name': 'mysite'})
        self.assertEqual(site.diff, {'login_base': ("foo", 'bar')})
        self.assertIn("login_base", site.changed_fields)
        self.assertEqual(site.has_field_changed("name"), False)
        self.assertEqual(site.has_field_changed("login_base"), True)

    def test_ORMWrapper_diff_after_save(self):
        orm = self.make_coreapi()
        site = orm.Site(name="mysite", login_base="foo")
        site.save()
        site = orm.Site.objects.first()

        self.assertEqual(site.diff, {})

        site.login_base = "bar"

        self.assertEqual(site.diff, {'login_base': ("foo", 'bar')})

        site.save()

        self.assertEqual(site.diff, {})

    def test_deleted_objects_all(self):
        orm = self.make_coreapi()
        orig_len_sites = len(orm.Site.objects.all())
        orig_len_deleted_sites = len(orm.Site.deleted_objects.all())
        site = orm.Site(name="mysite")
        site.save()
        site.delete()
        sites = orm.Site.objects.all()
        self.assertEqual(len(sites), orig_len_sites)
        deleted_sites = orm.Site.deleted_objects.all()
        self.assertEqual(len(deleted_sites), orig_len_deleted_sites+1)

    def test_deleted_objects_filter(self):
        orm = self.make_coreapi()
        with patch.object(orm.grpc_stub, "FilterTestModel", wraps=orm.grpc_stub.FilterTestModel) as filter:
            foo = orm.TestModel(name="foo")
            foo.save()
            foo.delete()

            # There should be no live objects
            objs = orm.TestModel.objects.filter(name = "foo")
            self.assertEqual(len(objs), 0)

            # There should be one deleted object
            deleted_objs = orm.TestModel.deleted_objects.filter(name = "foo")
            self.assertEqual(len(deleted_objs), 1)

            # Two calls, one for when we checked live objects, the other for when we checked deleted objects
            self.assertEqual(filter.call_count, 2)
            q = filter.call_args[0][0]

            # Now spy on the query that was generated, to make sure it looks like we expect
            self.assertEqual(q.kind, q.SYNCHRONIZER_DELETED_OBJECTS)
            self.assertEqual(len(q.elements), 1)
            self.assertEqual(q.elements[0].operator, q.elements[0].EQUAL)
            self.assertEqual(q.elements[0].sValue, "foo")


def main():
    global USE_FAKE_STUB
    global xos_grpc_client

    # Command-line argument of -R will cause this test to use a real grpc server
    # rather than the fake stub.

    if "-R" in sys.argv:
        USE_FAKE_STUB = False
        sys.argv.remove("-R")
        # Note: will leave lots of litter (users, sites, etc) behind in the database

    if USE_FAKE_STUB:
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

if __name__ == "__main__":
    main()
