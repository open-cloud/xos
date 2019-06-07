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

from __future__ import print_function

import os
import random
import string
import sys
import unittest

try:  # python 3
    from io import StringIO
    from unittest.mock import patch, MagicMock
except ImportError:  # python 2
    from StringIO import StringIO
    from mock import patch, MagicMock


# by default, use fake stub rather than real core
USE_FAKE_STUB = True

PARENT_DIR = os.path.join(os.path.dirname(__file__), "..")


class ORMTestBaseClass(unittest.TestCase):
    def setUp(self):
        from xosconfig import Config

        test_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
        config = os.path.join(test_path, "test_config.yaml")
        Config.clear()
        Config.init(config, "synchronizer-config-schema.yaml")
        if USE_FAKE_STUB:
            sys.path.append(PARENT_DIR)

        # Import these after config, in case they depend on config
        from xosapi.orm import ORMQuerySet, ORMLocalObjectManager

        self.ORMQuerySet = ORMQuerySet
        self.ORMLocalObjectManager = ORMLocalObjectManager

        self.orm = self.make_coreapi()

    def tearDown(self):
        if USE_FAKE_STUB:
            sys.path.remove(PARENT_DIR)

    def make_coreapi(self):
        if USE_FAKE_STUB:
            import xosapi.orm
            from fake_stub import FakeStub, FakeProtos, FakeObj

            xosapi.orm.import_convenience_methods()

            stub = FakeStub()
            api = xosapi.orm.ORMStub(
                stub=stub,
                package_name="xos",
                protos=FakeProtos(),
                empty=FakeObj,
                enable_backoff=False,
            )
            return api
        else:
            return xos_grpc_client.coreapi


class TestORMWrapper(ORMTestBaseClass):
    """ Tests for the ORMWrapper class """

    def test_ORMWrapper_fields_differ(self):
        testModel = self.orm.TestModel(intfield=7, stringfield="foo")
        self.assertTrue(testModel.fields_differ("a", "b"))
        self.assertFalse(testModel.fields_differ("a", "a"))

    def test_ORMWrapper_dict(self):
        testModel = self.orm.TestModel(intfield=7, stringfield="foo")

        self.assertDictEqual(testModel._dict, {"intfield": 7, "stringfield": "foo"})

    def test_ORMWrapper_new_diff(self):
        site = self.orm.Site(name="mysite")

        self.assertEqual(site.is_new, True)
        self.assertEqual(site._dict, {"name": "mysite"})
        self.assertEqual(site.diff, {})
        self.assertEqual(site.changed_fields, ["name"])
        self.assertEqual(site.has_field_changed("name"), False)
        self.assertEqual(site.has_field_changed("login_base"), False)
        self.assertEqual(site.has_changed, False)

        site.login_base = "bar"

        self.assertEqual(site._dict, {"login_base": "bar", "name": "mysite"})
        self.assertEqual(site.diff, {"login_base": (None, "bar")})
        self.assertIn("name", site.changed_fields)
        self.assertIn("login_base", site.changed_fields)
        self.assertEqual(site.has_field_changed("name"), False)
        self.assertEqual(site.has_field_changed("login_base"), True)
        self.assertEqual(site.has_changed, True)
        self.assertEqual(site.get_field_diff("login_base"), (None, "bar"))

    def test_ORMWrapper_existing_diff(self):
        site = self.orm.Site(name="mysite", login_base="foo")
        site.save()
        site = self.orm.Site.objects.first()

        self.assertEqual(site.is_new, False)
        self.assertEqual(site._dict, {"id": 1, "name": "mysite", "login_base": "foo"})
        self.assertEqual(site.diff, {})
        self.assertEqual(site.changed_fields, [])
        self.assertEqual(site.has_field_changed("name"), False)
        self.assertEqual(site.has_field_changed("login_base"), False)
        self.assertEqual(site.has_changed, False)

        site.login_base = "bar"

        self.assertEqual(site._dict, {"id": 1, "login_base": "bar", "name": "mysite"})
        self.assertEqual(site.diff, {"login_base": ("foo", "bar")})
        self.assertIn("login_base", site.changed_fields)
        self.assertEqual(site.has_field_changed("name"), False)
        self.assertEqual(site.has_field_changed("login_base"), True)
        self.assertEqual(site.has_changed, True)

    def test_ORMWrapper_diff_after_save(self):
        site = self.orm.Site(name="mysite", login_base="foo")
        site.save()
        site = self.orm.Site.objects.first()

        self.assertEqual(site.diff, {})

        site.login_base = "bar"

        self.assertEqual(site.diff, {"login_base": ("foo", "bar")})

        site.save()

        self.assertEqual(site.diff, {})

    def test_ORMWrapper_recompute_initial(self):
        """ For saved models, Recompute_initial should take recompute the set of initial values, removing all items
            from the diff set.
        """

        testModel = self.orm.TestModel()
        testModel.save()

        testModel.intfield = 9
        self.assertEqual(testModel.changed_fields, ["intfield"])

        testModel.recompute_initial()
        self.assertEqual(testModel.changed_fields, [])

    def test_ORMWrapper_save_changed_fields(self):
        testModel = self.orm.TestModel(intfield=7, stringfield="foo")
        testModel.save()

        testModel.intfield = 9

        with patch.object(
            self.orm.grpc_stub, "UpdateTestModel", wraps=self.orm.grpc_stub.UpdateTestModel
        ) as update:
            testModel.save_changed_fields()

            self.assertEqual(update.call_count, 1)
            self.assertIn("metadata", update.call_args[1])
            update_fields_arg = [
                x[1] for x in update.call_args[1]["metadata"] if x[0] == "update_fields"
            ]
            self.assertEqual(update_fields_arg, ["intfield"])

    def test_ORMWrapper_create_attr(self):
        testModel = self.orm.TestModel()
        testModel.create_attr("some_new_attribute", "foo")
        self.assertEqual(testModel.some_new_attribute, "foo")

    def test_ORMWrapper_get_generic_foreignkeys(self):
        """ Currently this is a placeholder that returns an empty list """

        testModel = self.orm.TestModel()
        self.assertEqual(testModel.get_generic_foreignkeys(), [])

    def test_ORMWrapper_gen_fkmap(self):
        """ TestModelTwo includes a foreignkey relation to TestModel, and the fkmap should contain that relation """

        testModelTwo = self.orm.TestModelTwo()

        self.assertDictEqual(
            testModelTwo.gen_fkmap(),
            {
                "testmodel": {
                    "kind": "fk",
                    "modelName": "TestModel",
                    "reverse_fieldName": "testmodeltwos",
                    "src_fieldName": "testmodel_id",
                }
            },
        )

    def test_ORMWrapper_gen_reverse_fkmap(self):
        """ TestModel includes a reverse relation back to TestModelTwo, and the reverse_fkmap should contain that
            relation.
        """

        testModel = self.orm.TestModel()

        self.assertDictEqual(
            testModel.gen_reverse_fkmap(),
            {
                "testmodeltwos": {
                    "modelName": "TestModelTwo",
                    "src_fieldName": "testmodeltwos_ids",
                    "writeable": False,
                }
            },
        )

    def test_ORMWrapper_fk_resolve(self):
        """ If we create a TestModelTwo that has a foreign key reference to a TestModel, then calling fk_resolve should
            return that model.
        """

        testModel = self.orm.TestModel()
        testModel.save()

        testModelTwo = self.orm.TestModelTwo(testmodel_id=testModel.id)

        testModel_resolved = testModelTwo.fk_resolve("testmodel")
        self.assertEqual(testModel_resolved.id, testModel.id)

        # the cache should have been populated
        self.assertIn(("testmodel", testModel_resolved), testModelTwo.cache.items())

    def test_ORMWrapper_reverse_fk_resolve(self):
        """ If a TestModelTwo has a relation to TestModel, then TestModel's reverse_fk should be resolvable to a list
            of TestModelTwo objects.
        """

        testModel = self.orm.TestModel()
        testModel.save()

        testModelTwo = self.orm.TestModelTwo(testmodel_id=testModel.id)
        testModelTwo.save()

        # fake_stub.py doesn't populate the reverse relations for us, so force what the server would have done...
        testModel._wrapped_class.testmodeltwos_ids = [testModelTwo.id]

        testModelTwos_resolved = testModel.reverse_fk_resolve("testmodeltwos")
        self.assertEqual(testModelTwos_resolved.count(), 1)

        # the reverse_cache should have been populated
        self.assertIn(
            ("testmodeltwos", testModelTwos_resolved), testModel.reverse_cache.items()
        )

    def test_ORMWrapper_fk_set(self):
        """ fk_set will set the testmodel field on TesTModelTwo to point to the TestModel. """

        testModel = self.orm.TestModel()
        testModel.save()

        testModelTwo = self.orm.TestModelTwo()

        testModelTwo.fk_set("testmodel", testModel)

        self.assertEqual(testModelTwo.testmodel_id, testModel.id)

    def test_ORMWrapper_post_save_fixups_remove(self):
        """ Apply a post_save_fixup that removes a reverse foreign key """

        testModel = self.orm.TestModel()
        testModel.save()

        testModelTwo = self.orm.TestModelTwo(testmodel_id=testModel.id)

        # fake_stub.py doesn't populate the reverse relations for us, so force what the server would have done...
        testModel._wrapped_class.testmodeltwos_ids = [testModelTwo.id]

        post_save_fixups = [
            {
                "src_fieldName": "testmodel",
                "dest_id": None,  # this field appears to not be used...
                "dest_model": testModel,
                "remove": True,
                "reverse_fieldName": "testmodeltwos",
            }
        ]

        testModelTwo.post_save_fixups = post_save_fixups
        testModelTwo.do_post_save_fixups()

        self.assertEqual(testModel._wrapped_class.testmodeltwos_ids, [])

    def test_ORMWrapper_post_save_fixups_add(self):
        """ Apply a post_save_fixup that adds a reverse foreign key """

        testModel = self.orm.TestModel()
        testModel.save()

        testModelTwo = self.orm.TestModelTwo(testmodel_id=testModel.id)
        testModelTwo.save()

        # Make sure the reverse_relation is unpopulated. This should be the case, as fake_stub.py() doesn't populate
        # the reverse relation. But let's be sure, in case someone fixes that.
        testModel._wrapped_class.testmodeltwos_ids = []

        post_save_fixups = [
            {
                "src_fieldName": "testmodel",
                "dest_id": None,  # this field appears to not be used...
                "dest_model": testModel,
                "remove": False,
                "reverse_fieldName": "testmodeltwos",
            }
        ]

        testModelTwo.post_save_fixups = post_save_fixups
        testModelTwo.do_post_save_fixups()

        self.assertEqual(testModel._wrapped_class.testmodeltwos_ids, [testModelTwo.id])

    def test_ORMWrapper_tologdict(self):
        """ Tologdict contains the model name and id, used for structured logging """
        testModel = self.orm.TestModel(intfield=7, stringfile="foo")

        self.assertDictEqual(
            testModel.tologdict(), {"model_name": "TestModel", "pk": 0}
        )

    def test_repr_name(self):
        s = self.orm.Slice(name="foo")
        self.assertNotEqual(s, None)
        self.assertEqual(repr(s), "<Slice: foo>")

    def test_repr_noname(self):
        s = self.orm.Slice()
        self.assertNotEqual(s, None)
        self.assertEqual(repr(s), "<Slice: id-0>")

    def test_str_name(self):
        s = self.orm.Slice(name="foo")
        self.assertNotEqual(s, None)
        self.assertEqual(str(s), "foo")

    def test_str_noname(self):
        s = self.orm.Slice()
        self.assertNotEqual(s, None)
        self.assertEqual(str(s), "Slice-0")

    def test_dumpstr_name(self):
        s = self.orm.Slice(name="foo")
        self.assertNotEqual(s, None)
        self.assertEqual(s.dumpstr(), 'name: "foo"\n')

    def test_dumpstr_noname(self):
        s = self.orm.Slice()
        self.assertNotEqual(s, None)
        self.assertEqual(s.dumpstr(), "")

    def test_dump(self):
        """ dump() is like dumpstr() but prints to stdout. Mock stdout by using a stringIO. """

        s = self.orm.Slice(name="foo")
        self.assertNotEqual(s, None)
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            s.dump()
            self.assertEqual(mock_stdout.getvalue(), 'name: "foo"\n\n')

    def test_invalidate_cache(self):
        testModel = self.orm.TestModel()

        # populate the caches with some placeholders we can test for
        testModel.cache = {"a": 1}
        testModel.reverse_cache = {"b": 2}

        testModel.invalidate_cache()

        self.assertEqual(testModel.cache, {})
        self.assertEqual(testModel.reverse_cache, {})

    def test_leaf_model_trivial(self):
        service = self.orm.Service(name="myservice")
        service.save()
        self.assertEqual(service.leaf_model_name, "Service")

    def test_leaf_model_descendant(self):
        onos_service = self.orm.ONOSService(name="myservice")
        onos_service.save()
        self.assertEqual(onos_service.model_name, "ONOSService")
        self.assertEqual(onos_service.leaf_model_name, "ONOSService")

        service = self.orm.Service.objects.get(id=onos_service.id)
        self.assertEqual(service.id, onos_service.id)
        self.assertEqual(service.model_name, "Service")
        self.assertEqual(service.leaf_model_name, "ONOSService")

        onos_service_cast = service.leaf_model
        self.assertEqual(onos_service_cast.model_name, "ONOSService")
        self.assertEqual(onos_service_cast.leaf_model_name, "ONOSService")
        self.assertEqual(onos_service_cast.id, onos_service.id)

    def test_ORMWrapper_model_name(self):
        testModel = self.orm.TestModel()
        self.assertEqual(testModel.model_name, "TestModel")

    def test_ORMWrapper_ansible_tag(self):
        """ Ansible_tag is used by old-style synchronizers. Deprecated. """

        testModel = self.orm.TestModel(id=7)

        self.assertEqual(testModel.ansible_tag, "TestModel_7")


class TestORMQuerySet(ORMTestBaseClass):
    """ Tests for high-level ORMQuerySet class """

    def test_ORMQuerySet_first_nonempty(self):
        qs = self.ORMQuerySet([1, 2, 3])
        self.assertEqual(qs.first(), 1)

    def test_ORMQuerySet_first_empty(self):
        qs = self.ORMQuerySet([])
        self.assertEqual(qs.first(), None)

    def test_ORMQuerySet_exists_nonempty(self):
        qs = self.ORMQuerySet([1, 2, 3])
        self.assertEqual(qs.exists(), True)

    def test_ORMQuerySet_exists_empty(self):
        qs = self.ORMQuerySet()
        self.assertEqual(qs.exists(), False)


class TestORMLocalObjectManager(ORMTestBaseClass):
    """ Tests for high-level ORMLocalObjectManager class """

    def test_ORMLocalObjectManager_nonempty(self):
        """ Test all(), first(), exists(), and count() together since they're all closely related. Use a nonempty
            list.
        """
        t = self.orm.TestModel()
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
        t = self.orm.TestModel()
        t.save()

        lobjs = self.ORMLocalObjectManager(t.stub, "TestModel", [], False)
        self.assertEqual(len(lobjs.all()), 0)
        self.assertEqual(lobjs.exists(), False)
        self.assertEqual(lobjs.count(), 0)
        self.assertEqual(lobjs.first(), None)

    def test_ORMLocalObjectManager_not_writeable(self):
        """ An ORMLocalObjectManager that is not writeable should throw exceptions on add() and remove() """
        t = self.orm.TestModel()
        t.save()

        lobjs = self.ORMLocalObjectManager(t.stub, "TestModel", [t.id], False)

        with self.assertRaises(Exception) as e:
            lobjs.add(123)
        self.assertEqual(str(e.exception), "Only ManyToMany lists are writeable")

        with self.assertRaises(Exception) as e:
            lobjs.remove(123)
        self.assertEqual(str(e.exception), "Only ManyToMany lists are writeable")

    def test_ORMLocalObjectManager_add(self):
        t = self.orm.TestModel()
        t.save()

        lobjs = self.ORMLocalObjectManager(t.stub, "TestModel", [], True)
        lobjs.add(t)
        self.assertEqual(lobjs.count(), 1)
        self.assertEqual(lobjs.first().id, t.id)

    def test_ORMLocalObjectManager_remove(self):
        t = self.orm.TestModel()
        t.save()

        lobjs = self.ORMLocalObjectManager(t.stub, "TestModel", [t.id], True)
        lobjs.remove(t)
        self.assertEqual(lobjs.count(), 0)


class TestORMObjectManager(ORMTestBaseClass):
    """ Tests for ORMObjectManager class """

    def test_wrap_single(self):
        wrapped_obj = self.orm.all_grpc_classes["Site"](name="mysite")
        orm_obj = self.orm.Site.objects.wrap_single(wrapped_obj)
        self.assertEqual(orm_obj._wrapped_class, wrapped_obj)

    def test_wrap_list(self):
        wrapped_obj = self.orm.all_grpc_classes["Site"](name="mysite")
        wrapped_list = MagicMock(items=[wrapped_obj])
        orm_objs = self.orm.Site.objects.wrap_list(wrapped_list)
        self.assertEqual(len(orm_objs), 1)
        self.assertEqual(orm_objs[0]._wrapped_class, wrapped_obj)

    def test_objects_all(self):
        orig_len_sites = len(self.orm.Site.objects.all())
        site = self.orm.Site(name="mysite")
        site.save()
        sites = self.orm.Site.objects.all()
        self.assertEqual(len(sites), orig_len_sites + 1)

    def test_objects_first(self):
        site = self.orm.Site(name="mysite")
        site.save()
        site = self.orm.Site.objects.first()
        self.assertNotEqual(site, None)

    def test_filter_query_iexact(self):
        with patch.object(self.orm.grpc_stub, "FilterTestModel", autospec=True) as filter:
            self.orm.TestModel.objects.filter(name__iexact="foo")
            self.assertEqual(filter.call_count, 1)
            q = filter.call_args[0][0]

            self.assertEqual(q.kind, q.DEFAULT)
            self.assertEqual(len(q.elements), 1)
            self.assertEqual(q.elements[0].operator, q.elements[0].IEXACT)
            self.assertEqual(q.elements[0].sValue, "foo")

    def test_filter_query_equal(self):
        with patch.object(self.orm.grpc_stub, "FilterTestModel", autospec=True) as filter:
            self.orm.TestModel.objects.filter(name="foo")
            self.assertEqual(filter.call_count, 1)
            q = filter.call_args[0][0]

            self.assertEqual(q.kind, q.DEFAULT)
            self.assertEqual(len(q.elements), 1)
            self.assertEqual(q.elements[0].operator, q.elements[0].EQUAL)
            self.assertEqual(q.elements[0].sValue, "foo")

    def test_filter_special(self):
        with patch.object(self.orm.grpc_stub, "FilterTestModel", autospec=True) as filter:
            self.orm.TestModel.objects.filter_special(kind=self.orm.TestModel.objects.SYNCHRONIZER_DIRTY_OBJECTS)
            self.assertEqual(filter.call_count, 1)
            q = filter.call_args[0][0]
            self.assertEqual(q.kind, q.SYNCHRONIZER_DIRTY_OBJECTS)

    def test_get(self):
        site = self.orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)
        got_site = self.orm.Site.objects.get(id=site.id)
        self.assertNotEqual(got_site, None)
        self.assertEqual(got_site.id, site.id)

    def test_new(self):
        site = self.orm.Site.objects.new(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)


class TestORMModelClass(ORMTestBaseClass):
    """ Tests for ORMModelClass class """

    def test_name(self):
        self.assertEqual(self.orm.Site.__name__, "Site")

    def test_content_type_id(self):
        self.assertNotEqual(self.orm.Site.content_type_id, None)

    def test_call(self):
        new_obj = self.orm.Site(name="mysite")
        self.assertNotEqual(new_obj, None)
        self.assertEqual(new_obj.name, "mysite")


class TestORM(ORMTestBaseClass):
    """ Tests for OMRStub and misc high-level ORM operations """

    def test_add_default_metadata(self):
        md = []
        self.orm.add_default_metadata(md)
        self.assertListEqual(md, [('caller_kind', 'grpcapi')])

    def test_make_ID(self):
        id_proto = self.orm.make_ID(123)
        self.assertEqual(id_proto.id, 123)

    def test_make_empty(self):
        empty_proto = self.orm.make_empty()
        self.assertNotEqual(empty_proto, None)

    def test_make_Query(self):
        query_proto = self.orm.make_Query()
        self.assertNotEqual(query_proto, None)
        self.assertTrue(hasattr(query_proto, "elements"))

    def test_listObjects(self):
        objs = self.orm.listObjects()
        self.assertIn("Slice", objs)

    def test_create(self):
        site = self.orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)

    def test_save_existing(self):
        orig_len_sites = len(self.orm.Site.objects.all())
        site = self.orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)

        # there should be one new site
        self.assertEqual(len(self.orm.Site.objects.all()), orig_len_sites + 1)

        # retrieve the site, and update it
        created_site_id = site.id
        site = self.orm.Site.objects.get(id=created_site_id)
        site.name = "mysitetwo"
        site.save()

        # the site_id should not have changed
        self.assertEqual(site.id, created_site_id)

        # there should still be only one new site
        self.assertEqual(len(self.orm.Site.objects.all()), orig_len_sites + 1)

        # the name should have changed
        self.assertEqual(self.orm.Site.objects.get(id=created_site_id).name, "mysitetwo")

    def test_delete(self):
        orig_len_sites = len(self.orm.Site.objects.all())
        site = self.orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)
        site.delete()
        sites = self.orm.Site.objects.all()
        self.assertEqual(len(sites), orig_len_sites)

    def test_content_type_map(self):
        self.assertTrue("Slice" in self.orm.content_type_map.values())
        self.assertTrue("Site" in self.orm.content_type_map.values())
        self.assertTrue("Tag" in self.orm.content_type_map.values())

    def test_foreign_key_get(self):
        site = self.orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)
        user = self.orm.User(
            email="fake_"
            + "".join(
                random.choice(string.ascii_uppercase + string.digits) for _ in range(10)
            ),
            site_id=site.id,
        )
        user.save()
        self.assertTrue(user.id > 0)
        slice = self.orm.Slice(name="mysite_foo", site_id=site.id, creator_id=user.id)
        slice.save()
        self.assertTrue(slice.id > 0)
        self.assertNotEqual(slice.site, None)
        self.assertEqual(slice.site.id, site.id)

    def test_foreign_key_set_with_invalidate(self):
        site = self.orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)
        user = self.orm.User(
            email="fake_"
            + "".join(
                random.choice(string.ascii_uppercase + string.digits) for _ in range(10)
            ),
            site_id=site.id,
        )
        user.save()
        self.assertTrue(user.id > 0)
        slice = self.orm.Slice(name="mysite_foo", site=site, creator_id=user.id)
        slice.save()
        slice.invalidate_cache()
        self.assertTrue(slice.id > 0)
        self.assertNotEqual(slice.site, None)
        self.assertEqual(slice.site.id, site.id)
        if not USE_FAKE_STUB:
            self.assertTrue(slice.id in slice.site.slices_ids)

    def test_foreign_key_set_without_invalidate(self):
        site = self.orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)
        user = self.orm.User(
            email="fake_"
            + "".join(
                random.choice(string.ascii_uppercase + string.digits) for _ in range(10)
            ),
            site_id=site.id,
        )
        user.save()
        self.assertTrue(user.id > 0)
        slice = self.orm.Slice(name="mysite_foo", site=site, creator_id=user.id)
        slice.save()
        self.assertTrue(slice.id > 0)
        self.assertNotEqual(slice.site, None)
        self.assertEqual(slice.site.id, site.id)
        if not USE_FAKE_STUB:
            self.assertTrue(slice.id in slice.site.slices_ids)
            ids_from_models = [x.id for x in slice.site.slices.all()]
            self.assertTrue(slice.id in ids_from_models)

    def test_foreign_key_reset(self):
        site = self.orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)
        user = self.orm.User(
            email="fake_"
            + "".join(
                random.choice(string.ascii_uppercase + string.digits) for _ in range(10)
            ),
            site_id=site.id,
        )
        user.save()
        self.assertTrue(user.id > 0)
        slice = self.orm.Slice(name="mysite_foo", site=site, creator_id=user.id)
        slice.save()
        self.assertTrue(slice.id > 0)
        self.assertNotEqual(slice.site, None)
        self.assertEqual(slice.site.id, site.id)
        if not USE_FAKE_STUB:
            self.assertTrue(slice.id in site.slices_ids)
            self.assertTrue(slice.id in slice.site.slices_ids)

        site2 = self.orm.Site(name="mysite2")
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
        site = self.orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)
        user = self.orm.User(
            email="fake_"
            + "".join(
                random.choice(string.ascii_uppercase + string.digits) for _ in range(10)
            ),
            site_id=site.id,
        )
        user.save()
        self.assertTrue(user.id > 0)
        slice = self.orm.Slice(name="mysite_foo", site=site, creator_id=user.id)
        slice.save()
        self.assertTrue(slice.id > 0)
        self.assertNotEqual(slice.site, None)
        self.assertEqual(slice.site.id, site.id)
        if not USE_FAKE_STUB:
            self.assertTrue(slice.id in site.slices_ids)
            self.assertTrue(slice.id in slice.site.slices_ids)

        site2 = self.orm.Site(name="mysite2")
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
        site = self.orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)
        user = self.orm.User(
            email="fake_"
            + "".join(
                random.choice(string.ascii_uppercase + string.digits) for _ in range(10)
            ),
            site_id=site.id,
        )
        user.save()
        self.assertTrue(user.id > 0)
        slice = self.orm.Slice(name="mysite_foo", site=site, creator_id=user.id)
        slice.save()
        self.assertTrue(slice.id > 0)
        self.assertNotEqual(slice.site, None)
        self.assertEqual(slice.site.id, site.id)
        if not USE_FAKE_STUB:
            self.assertTrue(slice.id in site.slices_ids)
            self.assertTrue(slice.id in slice.site.slices_ids)

        site2 = self.orm.Site(name="mysite2")
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
        site = self.orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)
        user = self.orm.User(
            email="fake_"
            + "".join(
                random.choice(string.ascii_uppercase + string.digits) for _ in range(10)
            ),
            site_id=site.id,
        )
        user.save()
        self.assertTrue(user.id > 0)
        slice = self.orm.Slice(
            name="mysite_foo", site=site, service=None, creator_id=user.id
        )
        slice.save()
        slice.invalidate_cache()
        self.assertTrue(slice.id > 0)
        self.assertEqual(slice.service, None)

    def test_foreign_key_set_null(self):
        site = self.orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)
        user = self.orm.User(
            email="fake_"
            + "".join(
                random.choice(string.ascii_uppercase + string.digits) for _ in range(10)
            ),
            site_id=site.id,
        )
        user.save()
        self.assertTrue(user.id > 0)
        service = self.orm.Service(name="myservice")
        service.save()
        self.assertTrue(service.id > 0)
        # start out slice.service is non-None
        slice = self.orm.Slice(
            name="mysite_foo", site=site, service=service, creator_id=user.id
        )
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
        service = self.orm.Service(name="myservice")
        service.save()
        site = self.orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)
        tag = self.orm.Tag(
            service=service,
            name="mytag",
            value="somevalue",
            content_type=site.self_content_type_id,
            object_id=site.id,
        )
        tag.save()
        self.assertTrue(tag.id > 0)
        self.assertNotEqual(tag.content_object, None)
        self.assertEqual(tag.content_object.id, site.id)

    def test_generic_foreign_key_get_decl(self):
        service = self.orm.Service(name="myservice")
        service.save()
        site = self.orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)
        tag = self.orm.Tag(
            service=service,
            name="mytag",
            value="somevalue",
            content_type=site.self_content_type_id + "_decl",
            object_id=site.id,
        )
        tag.save()
        self.assertTrue(tag.id > 0)
        self.assertNotEqual(tag.content_object, None)
        self.assertEqual(tag.content_object.id, site.id)

    def test_generic_foreign_key_get_bad_contenttype(self):
        service = self.orm.Service(name="myservice")
        service.save()
        site = self.orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)
        tag = self.orm.Tag(
            service=service,
            name="mytag",
            value="somevalue",
            content_type="does_not_exist",
            object_id=site.id,
        )
        tag.save()
        self.assertTrue(tag.id > 0)
        with self.assertRaises(Exception) as e:

            self.assertEqual(
                str(e.exception),
                "Content_type does_not_exist not found in self.content_type_map",
            )

    def test_generic_foreign_key_get_bad_id(self):
        service = self.orm.Service(name="myservice")
        service.save()
        site = self.orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)
        tag = self.orm.Tag(
            service=service,
            name="mytag",
            value="somevalue",
            content_type=site.self_content_type_id,
            object_id=4567,
        )
        tag.save()
        self.assertTrue(tag.id > 0)
        with self.assertRaises(Exception) as e:
            self.assertEqual(
                str(e.exception), "Object 4567 of model Site was not found"
            )

    def test_generic_foreign_key_set(self):
        service = self.orm.Service(name="myservice")
        service.save()
        site = self.orm.Site(name="mysite")
        site.save()
        self.assertTrue(site.id > 0)
        tag = self.orm.Tag(service=service, name="mytag", value="somevalue")
        tag.content_object = site
        tag.invalidate_cache()
        self.assertEqual(tag.content_type, site.self_content_type_id)
        self.assertEqual(tag.object_id, site.id)
        tag.save()
        self.assertTrue(tag.id > 0)
        self.assertNotEqual(tag.content_object, None)
        self.assertEqual(tag.content_object.id, site.id)

    def test_field_null(self):
        """ In a saved object, if a nullable field is left set to None, make sure the ORM returns None """

        tm = self.orm.TestModel()
        tm.save()

        tm = self.orm.TestModel.objects.all()[0]
        self.assertFalse(tm._wrapped_class.HasField("intfield"))
        self.assertEqual(tm.intfield, None)

    def test_field_null_new(self):
        """ For models that haven't been saved yet, reading the field should return the gRPC default """

        tm = self.orm.TestModel()

        self.assertEqual(tm.intfield, 0)

    def test_field_non_null(self):
        """ In a saved object, if a nullable field is set to a value, then make sure the ORM returns the value """

        tm = self.orm.TestModel(intfield=3)
        tm.save()

        tm = self.orm.TestModel.objects.all()[0]
        self.assertEqual(tm.intfield, 3)

    def test_field_set_null(self):
        """ Setting a field to None is not allowed """

        tm = self.orm.TestModel()
        with self.assertRaises(Exception) as e:
            tm.intfile = None
        self.assertEqual(
            str(e.exception),
            "Setting a non-foreignkey field to None is not supported",
        )

    def test_deleted_objects_all(self):
        orig_len_sites = len(self.orm.Site.objects.all())
        orig_len_deleted_sites = len(self.orm.Site.deleted_objects.all())
        site = self.orm.Site(name="mysite")
        site.save()
        site.delete()
        sites = self.orm.Site.objects.all()
        self.assertEqual(len(sites), orig_len_sites)
        deleted_sites = self.orm.Site.deleted_objects.all()
        self.assertEqual(len(deleted_sites), orig_len_deleted_sites + 1)

    def test_deleted_objects_filter(self):
        with patch.object(
            self.orm.grpc_stub, "FilterTestModel", wraps=self.orm.grpc_stub.FilterTestModel
        ) as filter:
            foo = self.orm.TestModel(name="foo")
            foo.save()
            foo.delete()

            # There should be no live objects
            objs = self.orm.TestModel.objects.filter(name="foo")
            self.assertEqual(len(objs), 0)

            # There should be one deleted object
            deleted_objs = self.orm.TestModel.deleted_objects.filter(name="foo")
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

        from xosapi import xos_grpc_client

        print("Using xos-client library and core server")

        def test_callback():
            try:
                sys.argv = sys.argv[
                    :1
                ]
                # unittest does not like xos_grpc_client's command line
                # arguments (TODO: find a cooperative approach)
                unittest.main()
            except SystemExit as e:
                global exitStatus
                exitStatus = e.code

        xos_grpc_client.start_api_parseargs(test_callback)

        sys.exit(exitStatus)


if __name__ == "__main__":
    main()
