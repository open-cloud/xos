
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
import string
import sys
import unittest
from mock import patch, ANY
from StringIO import StringIO

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

        # Import these after config, in case they depend on config
        from xosapi.orm import ORMQuerySet, ORMLocalObjectManager
        self.ORMQuerySet = ORMQuerySet
        self.ORMLocalObjectManager = ORMLocalObjectManager

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

    def test_dump(self):
        """ dump() is like dumpstr() but prints to stdout. Mock stdout by using a stringIO. """

        orm = self.make_coreapi()
        s = orm.Slice(name="foo")
        self.assertNotEqual(s, None)
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            s.dump()
            self.assertEqual(mock_stdout.getvalue(), 'name: "foo"\n\n')

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

    def test_invalidate_cache(self):
        orm = self.make_coreapi()
        testModel = orm.TestModel()

        # populate the caches with some placeholders we can test for
        testModel.cache = {"a": 1}
        testModel.reverse_cache = {"b": 2}

        testModel.invalidate_cache()

        self.assertEqual(testModel.cache, {})
        self.assertEqual(testModel.reverse_cache, {})

    def test_save_new(self):
        orm = self.make_coreapi()
        orig_len_sites = len(orm.Site.objects.all())
        site = orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)

    def test_save_existing(self):
        orm = self.make_coreapi()
        orig_len_sites = len(orm.Site.objects.all())
        site = orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)

        # there should be one new site
        self.assertEqual(len(orm.Site.objects.all()), orig_len_sites+1)

        # retrieve the site, and update it
        created_site_id = site.id
        site = orm.Site.objects.get(id=created_site_id)
        site.name="mysitetwo"
        site.save()

        # the site_id should not have changed
        self.assertEqual(site.id, created_site_id)

        # there should still be only one new site
        self.assertEqual(len(orm.Site.objects.all()), orig_len_sites + 1)

        # the name should have changed
        self.assertEqual(orm.Site.objects.get(id=created_site_id).name, "mysitetwo")

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

    def test_ORMWrapper_dict(self):
        orm = self.make_coreapi()

        testModel = orm.TestModel(intfield=7, stringfield="foo")

        self.assertDictEqual(testModel._dict, {"intfield": 7, "stringfield": "foo"})

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

    def test_ORMWrapper_recompute_initial(self):
        """ For saved models, Recompute_initial should take recompute the set of initial values, removing all items
            from the diff set.
        """

        orm = self.make_coreapi()

        testModel = orm.TestModel()
        testModel.save()

        testModel.intfield = 9
        self.assertEqual(testModel.changed_fields, ["intfield"])

        testModel.recompute_initial()
        self.assertEqual(testModel.changed_fields, [])

    def test_ORMWrapper_create_attr(self):
        orm = self.make_coreapi()

        testModel = orm.TestModel()
        testModel.create_attr("some_new_attribute", "foo")
        self.assertEqual(testModel.some_new_attribute, "foo")

    def test_ORMWrapper_save_changed_fields(self):
        orm = self.make_coreapi()

        testModel = orm.TestModel(intfield=7, stringfield="foo")
        testModel.save()

        testModel.intfield=9

        with patch.object(orm.grpc_stub, "UpdateTestModel", wraps=orm.grpc_stub.UpdateTestModel) as update:
            testModel.save_changed_fields()
            update.assert_called_with(ANY, metadata=[("update_fields", "intfield"), ANY])

    def test_ORMWrapper_get_generic_foreignkeys(self):
        """ Currently this is a placeholder that returns an empty list """

        orm = self.make_coreapi()

        testModel = orm.TestModel()
        self.assertEqual(testModel.get_generic_foreignkeys(), [])

    def test_ORMWrapper_gen_fkmap(self):
        """ TestModelTwo includes a foreignkey relation to TestModel, and the fkmap should contain that relation """

        orm = self.make_coreapi()

        testModelTwo = orm.TestModelTwo()

        self.assertDictEqual(testModelTwo.gen_fkmap(),
                             {'testmodel': {'kind': 'fk',
                                            'modelName': 'TestModel',
                                            'reverse_fieldName': 'testmodeltwos',
                                            'src_fieldName': 'testmodel_id'}})

    def test_ORMWrapper_gen_reverse_fkmap(self):
        """ TestModel includes a reverse relation back to TestModelTwo, and the reverse_fkmap should contain that
            relation.
        """

        orm = self.make_coreapi()

        testModel = orm.TestModel()

        self.assertDictEqual(testModel.gen_reverse_fkmap(),
                             {'testmodeltwos': {'modelName': 'TestModelTwo',
                                                'src_fieldName': 'testmodeltwos_ids',
                                                'writeable': False}})

    def test_ORMWrapper_fk_resolve(self):
        """ If we create a TestModelTwo that has a foreign key reference to a TestModel, then calling fk_resolve should
            return that model.
        """

        orm = self.make_coreapi()

        testModel = orm.TestModel()
        testModel.save()

        testModelTwo = orm.TestModelTwo(testmodel_id=testModel.id)

        testModel_resolved = testModelTwo.fk_resolve("testmodel")
        self.assertEqual(testModel_resolved.id, testModel.id)

    def test_ORMWrapper_reverse_fk_resolve(self):
        """ If a TestModelTwo has a relation to TestModel, then TestModel's reverse_fk should be resolvable to a list
            of TestModelTwo objects.
        """

        orm = self.make_coreapi()

        testModel = orm.TestModel()
        testModel.save()

        testModelTwo = orm.TestModelTwo(testmodel_id=testModel.id)
        testModelTwo.save()

        # fake_stub.py doesn't populate the reverse relations for us, so force what the server would have done...
        testModel._wrapped_class.testmodeltwos_ids = [testModelTwo.id]

        testModelTwos_resolved = testModel.reverse_fk_resolve("testmodeltwos")
        self.assertEqual(testModelTwos_resolved.count(), 1)

    def test_ORMWrapper_fk_set(self):
        """ fk_set will set the testmodel field on TesTModelTwo to point to the TestModel. """

        orm = self.make_coreapi()

        testModel = orm.TestModel()
        testModel.save()

        testModelTwo = orm.TestModelTwo()

        testModelTwo.fk_set("testmodel", testModel)

        self.assertEqual(testModelTwo.testmodel_id, testModel.id)

    def test_ORMWrapper_post_save_fixups_remove(self):
        """ Apply a post_save_fixup that removes a reverse foreign key """

        orm = self.make_coreapi()

        testModel = orm.TestModel()
        testModel.save()

        testModelTwo = orm.TestModelTwo(testmodel_id=testModel.id)

        # fake_stub.py doesn't populate the reverse relations for us, so force what the server would have done...
        testModel._wrapped_class.testmodeltwos_ids = [testModelTwo.id]

        post_save_fixups = [{"src_fieldName": "testmodel",
                             "dest_id": None, # this field appears to not be used...
                             "dest_model": testModel,
                             "remove": True,
                             "reverse_fieldName": "testmodeltwos"}]

        testModelTwo.post_save_fixups = post_save_fixups
        testModelTwo.do_post_save_fixups()

        self.assertEqual(testModel._wrapped_class.testmodeltwos_ids, [])

    def test_ORMWrapper_post_save_fixups_add(self):
        """ Apply a post_save_fixup that adds a reverse foreign key """

        orm = self.make_coreapi()

        testModel = orm.TestModel()
        testModel.save()

        testModelTwo = orm.TestModelTwo(testmodel_id=testModel.id)
        testModelTwo.save()

        # Make sure the reverse_relation is unpopulated. This should be the case, as fake_stub.py() doesn't populate
        # the reverse relation. But let's be sure, in case someone fixes that.
        testModel._wrapped_class.testmodeltwos_ids = []

        post_save_fixups = [{"src_fieldName": "testmodel",
                             "dest_id": None, # this field appears to not be used...
                             "dest_model": testModel,
                             "remove": False,
                             "reverse_fieldName": "testmodeltwos"}]

        testModelTwo.post_save_fixups = post_save_fixups
        testModelTwo.do_post_save_fixups()

        self.assertEqual(testModel._wrapped_class.testmodeltwos_ids, [testModelTwo.id])


    def test_ORMWrapper_tologdict(self):
        """ Tologdict contains the model name and id, used for structured logging """
        orm = self.make_coreapi()

        testModel = orm.TestModel(intfield=7, stringfile="foo")

        self.assertDictEqual(testModel.tologdict(), {'model_name': 'TestModel', 'pk': 0})

    def test_ORMWrapper_ansible_tag(self):
        """ Ansible_tag is used by old-style synchronizers. Deprecated. """

        orm = self.make_coreapi()

        testModel = orm.TestModel(id=7)

        self.assertEqual(testModel.ansible_tag, "TestModel_7")


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

    def test_ORMQuerySet_first_nonempty(self):
        qs = self.ORMQuerySet([1,2,3])
        self.assertEqual(qs.first(), 1)

    def test_ORMQuerySet_first_empty(self):
        qs = self.ORMQuerySet([])
        self.assertEqual(qs.first(), None)

    def test_ORMQuerySet_exists_nonempty(self):
        qs = self.ORMQuerySet([1,2,3])
        self.assertEqual(qs.exists(), True)

    def test_ORMQuerySet_exists_empty(self):
        qs = self.ORMQuerySet()
        self.assertEqual(qs.exists(), False)

    def test_ORMLocalObjectManager_nonempty(self):
        """ Test all(), first(), exists(), and count() together since they're all closely related. Use a nonempty
            list.
        """
        orm = self.make_coreapi()

        t = orm.TestModel()
        t.save()

        lobjs = self.ORMLocalObjectManager(t.stub, "TestModel", [t.id], False)
        self.assertEqual(len(lobjs.all()), 1)
        self.assertEqual(lobjs.all()[0].id, t.id)
        self.assertEqual(lobjs.exists(), True)
        self.assertEqual(lobjs.count(), 1)
        self.assertEqual(lobjs.first().id, t.id)

    def test_ORMLocalObjectManager_empty(self):
        """ Test all(), first(), exists(), and count() together since they're all closely related. Use an empty
            list.
        """
        orm = self.make_coreapi()

        t = orm.TestModel()
        t.save()

        lobjs = self.ORMLocalObjectManager(t.stub, "TestModel", [], False)
        self.assertEqual(len(lobjs.all()), 0)
        self.assertEqual(lobjs.exists(), False)
        self.assertEqual(lobjs.count(), 0)
        self.assertEqual(lobjs.first(), None)

    def test_ORMLocalObjectManager_not_writeable(self):
        """ An ORMLocalObjectManager that is not writeable should throw exceptions on add() and remove() """
        orm = self.make_coreapi()

        t = orm.TestModel()
        t.save()

        lobjs = self.ORMLocalObjectManager(t.stub, "TestModel", [t.id], False)

        with self.assertRaises(Exception) as e:
            lobjs.add(123)
        self.assertEqual(e.exception.message, "Only ManyToMany lists are writeable")

        with self.assertRaises(Exception) as e:
            lobjs.remove(123)
        self.assertEqual(e.exception.message, "Only ManyToMany lists are writeable")

    def test_ORMLocalObjectManager_add(self):
        orm = self.make_coreapi()

        t = orm.TestModel()
        t.save()

        lobjs = self.ORMLocalObjectManager(t.stub, "TestModel", [], True)
        lobjs.add(t)
        self.assertEqual(lobjs.count(), 1)
        self.assertEqual(lobjs.first().id, t.id)

    def test_ORMLocalObjectManager_remove(self):
        orm = self.make_coreapi()

        t = orm.TestModel()
        t.save()

        lobjs = self.ORMLocalObjectManager(t.stub, "TestModel", [t.id], True)
        lobjs.remove(t)
        self.assertEqual(lobjs.count(), 0)

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
