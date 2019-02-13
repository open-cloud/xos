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

import json
import os
import shutil
import tempfile
import unittest
from mock import patch, MagicMock, Mock

from xosconfig import Config


class DynamicLoadItem:
    def __init__(self, **kwargs):
        for (k, v) in kwargs.items():
            setattr(self, k, v)


class DynamicLoadRequest:
    def __init__(self, **kwargs):
        self.xprotos = []
        self.decls = []
        self.attics = []
        self.migrations = []
        for (k, v) in kwargs.items():
            setattr(self, k, v)


class DynamicUnloadRequest:
    REQUIRE_CLEAN = 0
    AUTOMATICALLY_CLEAN = 1
    PURGE = 2

    def __init__(self, **kwargs):
        self.cleanup_behavior = self.REQUIRE_CLEAN
        for (k, v) in kwargs.items():
            setattr(self, k, v)


class TestDynamicBuild(unittest.TestCase):
    def setUp(self):
        global dynamicbuild

        config = os.path.abspath(
            os.path.dirname(os.path.realpath(__file__)) + "/test_config.yaml"
        )
        Config.clear()  # in case left unclean by a previous test case
        Config.init(config)

        import dynamicbuild

        self.base_dir = tempfile.mkdtemp()
        self.example_xproto = """option app_label = "exampleservice";
option name = "exampleservice";

message ExampleService (Service){
    option verbose_name = "Example Service";
    required string service_message = 1 [help_text = "Service Message to Display",
      max_length = 254, null = False, db_index = False, blank = False];
}

message Color (XOSBase){
     option verbose_name = "Color";
     required string name = 1 [help_text = "Name for this color", db_index = False,
       max_length = 256, null = False, blank = False];
     required string html_code = 2 [help_text = "Code for this color", db_index = False,
       max_length = 256, null = False, blank = False];
}

message ExampleServiceInstance (TenantWithContainer){
     option verbose_name = "Example Service Instance";
     required string tenant_message = 1 [help_text = "Tenant Message to Display",
       max_length = 254, null = False, db_index = False, blank = False];
     optional manytoone foreground_color->Color:serviceinstance_foreground_colors = 3 [db_index = True,
       null = True, blank = True];
     optional manytoone background_color->Color:serviceinstance_background_colors = 3 [db_index = True,
       null = True, blank = True];
}

message EmbeddedImage (XOSBase){
     option verbose_name = "Embedded Image";
     required string name = 1 [help_text = "Name for this image", db_index = False,
       max_length = 256, null = False, blank = False];
     required string url = 2 [help_text = "URL for this image", db_index = False,
       max_length = 256, null = False, blank = False];
     optional manytoone serviceinstance->ExampleServiceInstance:embedded_images = 3 [db_index = True,
       null = True, blank = True];
}
        """

        self.example_xproto_item = DynamicLoadItem(
            filename="exampleservice.xproto", contents=self.example_xproto
        )

        self.example_request = DynamicLoadRequest(
            name="exampleservice",
            version="1",
            xprotos=[self.example_xproto_item],
            convenience_methods=[],
        )

        self.example_unload_request = DynamicUnloadRequest(
            name="exampleservice", version="1"
        )

        self.builder = dynamicbuild.DynamicBuilder(base_dir=self.base_dir)

    def tearDown(self):
        if os.path.abspath(self.base_dir).startswith(
            "/tmp"
        ):  # be paranoid about recursive deletes
            shutil.rmtree(self.base_dir)

    def test_pre_validate_file(self):
        self.builder.pre_validate_file(self.example_xproto_item)

        # dashes are okay
        item = DynamicLoadItem(
            filename="example-service.xproto", contents=self.example_xproto
        )
        self.builder.pre_validate_file(item)

        # undestcores are okay
        item = DynamicLoadItem(
            filename="example_service.xproto", contents=self.example_xproto
        )
        self.builder.pre_validate_file(item)

        # mixed case is okay
        item = DynamicLoadItem(
            filename="ExampleService.xproto", contents=self.example_xproto
        )
        self.builder.pre_validate_file(item)

        # no "." is still considered valid
        item = DynamicLoadItem(
            filename="ExampleServicexproto", contents=self.example_xproto
        )
        self.builder.pre_validate_file(item)

    def test_pre_validate_file_illegal_char(self):
        item = DynamicLoadItem(
            filename="/exampleservice.xproto", contents=self.example_xproto
        )
        with self.assertRaises(Exception) as e:
            self.builder.pre_validate_file(item)
        self.assertEqual(
            str(e.exception), "illegal character in filename /exampleservice.xproto"
        )

        item = DynamicLoadItem(
            filename="\"exampleservice.xproto\"", contents=self.example_xproto
        )
        with self.assertRaises(Exception) as e:
            self.builder.pre_validate_file(item)
        self.assertEqual(
            str(e.exception), "illegal character in filename \"exampleservice.xproto\""
        )

        item = DynamicLoadItem(
            filename="'exampleservice.xproto'", contents=self.example_xproto
        )
        with self.assertRaises(Exception) as e:
            self.builder.pre_validate_file(item)
        self.assertEqual(
            str(e.exception), "illegal character in filename 'exampleservice.xproto'"
        )

        item = DynamicLoadItem(
            filename="example service.xproto", contents=self.example_xproto
        )
        with self.assertRaises(Exception) as e:
            self.builder.pre_validate_file(item)
        self.assertEqual(
            str(e.exception), "illegal character in filename example service.xproto"
        )

        item = DynamicLoadItem(
            filename="", contents=self.example_xproto
        )
        with self.assertRaises(Exception) as e:
            self.builder.pre_validate_file(item)
        self.assertEqual(
            str(e.exception), "illegal character in filename "
        )

    def test_pre_validate_models(self):
        self.builder.pre_validate_models(self.example_request)

    def test_generate_request_hash(self):
        hash = self.builder.generate_request_hash(self.example_request, state="load")
        self.assertEqual(hash, "44951ff370c565c796f05f7c3fce67f9a4d4d3f6")

    def test_handle_loadmodels_request(self):
        with patch.object(
            dynamicbuild.DynamicBuilder, "save_models", wraps=self.builder.save_models
        ) as save_models, patch.object(
            dynamicbuild.DynamicBuilder,
            "run_xosgenx_service",
            wraps=self.builder.run_xosgenx_service,
        ) as run_xosgenx_service, patch.object(
            dynamicbuild.DynamicBuilder,
            "remove_service",
            wraps=self.builder.remove_service,
        ) as remove_service:
            result = self.builder.handle_loadmodels_request(self.example_request)

            save_models.assert_called()
            run_xosgenx_service.assert_called()
            remove_service.assert_not_called()

            self.assertEqual(result, self.builder.SUCCESS)

            self.assertTrue(os.path.exists(self.builder.manifest_dir))
            self.assertTrue(
                os.path.exists(
                    os.path.join(self.builder.manifest_dir, "exampleservice.json")
                )
            )

            service_dir = os.path.join(self.base_dir, "services", "exampleservice")

            self.assertTrue(os.path.exists(service_dir))
            self.assertTrue(os.path.exists(os.path.join(service_dir, "__init__.py")))
            self.assertTrue(os.path.exists(os.path.join(service_dir, "models.py")))
            self.assertTrue(os.path.exists(os.path.join(service_dir, "security.py")))

            manifest = json.loads(
                open(
                    os.path.join(self.builder.manifest_dir, "exampleservice.json"), "r"
                ).read()
            )
            self.assertEqual(manifest.get("state"), "load")

    def test_handle_loadmodels_request_with_migrations(self):
        with patch.object(
            dynamicbuild.DynamicBuilder, "save_models", wraps=self.builder.save_models
        ) as save_models, patch.object(
            dynamicbuild.DynamicBuilder,
            "run_xosgenx_service",
            wraps=self.builder.run_xosgenx_service,
        ) as run_xosgenx_service, patch.object(
            dynamicbuild.DynamicBuilder,
            "remove_service",
            wraps=self.builder.remove_service,
        ) as remove_service:
            migration1_contents = "print 'one'"
            migration1 = DynamicLoadItem(
                filename="migration1.py", contents=migration1_contents
            )
            migration2_contents = "print 'one'"
            migration2 = DynamicLoadItem(
                filename="migration2.py", contents=migration2_contents
            )

            self.example_request.migrations = [migration1, migration2]

            result = self.builder.handle_loadmodels_request(self.example_request)

            save_models.assert_called()
            run_xosgenx_service.assert_called()
            remove_service.assert_not_called()

            self.assertEqual(result, self.builder.SUCCESS)

            self.assertTrue(os.path.exists(self.builder.manifest_dir))
            self.assertTrue(
                os.path.exists(
                    os.path.join(self.builder.manifest_dir, "exampleservice.json")
                )
            )

            service_dir = os.path.join(self.base_dir, "services", "exampleservice")

            self.assertTrue(os.path.exists(service_dir))
            self.assertTrue(os.path.exists(os.path.join(service_dir, "__init__.py")))
            self.assertTrue(os.path.exists(os.path.join(service_dir, "models.py")))
            self.assertTrue(os.path.exists(os.path.join(service_dir, "security.py")))

            self.assertTrue(os.path.exists(os.path.join(service_dir, "migrations", "migration1.py")))
            self.assertTrue(os.path.exists(os.path.join(service_dir, "migrations", "migration2.py")))
            self.assertTrue(os.path.exists(os.path.join(service_dir, "migrations", "__init__.py")))

            manifest = json.loads(
                open(
                    os.path.join(self.builder.manifest_dir, "exampleservice.json"), "r"
                ).read()
            )
            self.assertEqual(manifest.get("state"), "load")

            self.assertEqual(
                manifest.get("migrations"),
                [{u'filename': u'migration1.py'}, {u'filename': u'migration2.py'}])

    def test_handle_unloadmodels_request(self):
        with patch.object(
            dynamicbuild.DynamicBuilder, "save_models", wraps=self.builder.save_models
        ) as save_models, patch.object(
            dynamicbuild.DynamicBuilder,
            "run_xosgenx_service",
            wraps=self.builder.run_xosgenx_service,
        ) as run_xosgenx_service, patch.object(
            dynamicbuild.DynamicBuilder,
            "remove_service",
            wraps=self.builder.remove_service,
        ) as remove_service:
            result = self.builder.handle_unloadmodels_request(
                self.example_unload_request,
                {}
            )

            save_models.assert_called()
            run_xosgenx_service.assert_not_called()
            remove_service.assert_called()

            self.assertEqual(result, self.builder.SUCCESS)

            self.assertTrue(os.path.exists(self.builder.manifest_dir))
            self.assertTrue(
                os.path.exists(
                    os.path.join(self.builder.manifest_dir, "exampleservice.json")
                )
            )

            manifest = json.loads(
                open(
                    os.path.join(self.builder.manifest_dir, "exampleservice.json"), "r"
                ).read()
            )
            self.assertEqual(manifest.get("state"), "unload")

    def test_handle_unloadmodels_request_live_models(self):
        with patch.object(
            dynamicbuild.DynamicBuilder, "save_models", wraps=self.builder.save_models
        ) as save_models, patch.object(
            dynamicbuild.DynamicBuilder,
            "remove_service",
            wraps=self.builder.remove_service,
        ) as remove_service:
            someobject = Mock()
            somemodel = MagicMock()
            somemodel.objects.all.return_value = [someobject]
            somemodel.objects.exists.return_value = True

            # Test with cleanup_behavior = REQUIRE_CLEAN

            result = self.builder.handle_unloadmodels_request(
                self.example_unload_request,
                {"somemodel": somemodel, }
            )

            save_models.assert_not_called()
            remove_service.assert_not_called()

            self.assertEqual(result, self.builder.ERROR_LIVE_MODELS)

            # Test with cleanup_behavior = AUTOMATICALLY_CLEAN

            self.example_unload_request.cleanup_behavior = self.example_unload_request.AUTOMATICALLY_CLEAN
            somemodel.objects.exists.return_value = False
            somemodel.deleted_objects.all.return_value = [someobject]

            result = self.builder.handle_unloadmodels_request(
                self.example_unload_request,
                {"somemodel": somemodel, }
            )

            save_models.assert_not_called()
            remove_service.assert_not_called()

            self.assertEqual(result, self.builder.TRYAGAIN)

            # Test with cleanup_behavior = PURGE

            self.example_unload_request.cleanup_behavior = self.example_unload_request.PURGE
            somemodel.objects.exists.return_value = False
            somemodel.deleted_objects.all.return_value = [someobject]

            result = self.builder.handle_unloadmodels_request(
                self.example_unload_request,
                {"somemodel": somemodel, }
            )

            save_models.assert_called()
            remove_service.assert_called()

            self.assertEqual(result, self.builder.SUCCESS)

    def test_handle_unloadmodels_request_softdeleted_models(self):
        with patch.object(
            dynamicbuild.DynamicBuilder, "save_models", wraps=self.builder.save_models
        ) as save_models, patch.object(
            dynamicbuild.DynamicBuilder,
            "remove_service",
            wraps=self.builder.remove_service,
        ) as remove_service:
            someobject = Mock()
            somemodel = MagicMock()
            somemodel.objects.all.return_value = []
            somemodel.objects.exists.return_value = False
            somemodel.deleted_objects.all.return_value = [someobject]

            # Test with cleanup_behavior = REQUIRE_CLEAN

            result = self.builder.handle_unloadmodels_request(
                self.example_unload_request,
                {"somemodel": somemodel, }
            )

            save_models.assert_not_called()
            remove_service.assert_not_called()

            self.assertEqual(result, self.builder.ERROR_DELETION_IN_PROGRESS)

    def test_handle_loadmodels_request_twice(self):
        result = self.builder.handle_loadmodels_request(self.example_request)
        self.assertEqual(result, self.builder.SUCCESS)

        result = self.builder.handle_loadmodels_request(self.example_request)
        self.assertEqual(result, self.builder.SUCCESS_NOTHING_CHANGED)

    def test_save_models(self):
        manifest = self.builder.save_models(self.example_request, state="load")

        dynamic_dir = os.path.join(self.base_dir, "dynamic_services", "exampleservice")
        service_dir = os.path.join(self.base_dir, "services", "exampleservice")

        self.assertEqual(manifest["name"], self.example_request.name)
        self.assertEqual(manifest["version"], self.example_request.version)
        self.assertEqual(manifest["hash"], "44951ff370c565c796f05f7c3fce67f9a4d4d3f6")
        self.assertEqual(manifest["dir"], dynamic_dir)
        self.assertEqual(manifest["dest_dir"], service_dir)
        self.assertEqual(len(manifest["xprotos"]), 1)

    def test_save_models_precomputed_hash(self):
        manifest = self.builder.save_models(
            self.example_request, state="load", hash="1234"
        )

        dynamic_dir = os.path.join(self.base_dir, "dynamic_services", "exampleservice")
        service_dir = os.path.join(self.base_dir, "services", "exampleservice")

        self.assertEqual(manifest["name"], self.example_request.name)
        self.assertEqual(manifest["version"], self.example_request.version)
        self.assertEqual(manifest["hash"], "1234")
        self.assertEqual(manifest["dir"], dynamic_dir)
        self.assertEqual(manifest["dest_dir"], service_dir)
        self.assertEqual(len(manifest["xprotos"]), 1)

    def test_pre_validate_python_good(self):
        good_python = """
import foo

x=1
y="abc"
"""
        python_item = DynamicLoadItem(filename="somefile.py", contents=good_python)

        self.builder.pre_validate_python(python_item)

    def test_pre_validate_python_bad(self):
        bad_python = """
import foo

this is not valid code
y="abc"
"""
        python_item = DynamicLoadItem(filename="somefile.py", contents=bad_python)

        with self.assertRaises(Exception) as e:
            self.builder.pre_validate_python(python_item)

        self.assertEqual(
            str(e.exception), "python file somefile.py failed compile test"
        )


def main():
    unittest.main()


if __name__ == "__main__":
    main()
