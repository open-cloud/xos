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

from __future__ import absolute_import
import unittest
from mock import patch, Mock, MagicMock

from io import StringIO
import functools
import os
import sys

# Python 3 renamed __builtin__ -> builtins
# py_builtins is used to help with mocking 'open'
try:
    import builtins
    py_builtins = "builtins"
except ImportError:
    import __builtin__ as builtins
    py_builtins = "__builtin__"

test_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))


def mock_listdir(dir_map, dir):
    """ mock os.listdir() """
    return dir_map.get(dir, [])


def mock_exists(file_map, fn):
    """ mock os.path.exists() """
    return fn in file_map


def mock_open(orig_open, file_map, fn, *args, **kwargs):
    """ mock file open() """
    if fn in file_map:
        return StringIO(file_map[fn])
    else:
        return orig_open(fn, *args, **kwargs)


class ItemList(object):
    """ mock the various items within a LoadModelsRequest protobuf """

    def __init__(self):
        self.items = []

    def add(self):
        item = Mock()
        self.items.append(item)
        return item


class MockLoadModelsRequest(object):
    """ mock a LoadModelsRequest protobuf """

    def __init__(self, *args, **kwargs):
        for (k, v) in kwargs.items():
            setattr(self, k, v)
        self.xprotos = ItemList()
        self.decls = ItemList()
        self.attics = ItemList()
        self.convenience_methods = ItemList()
        self.migrations = ItemList()


class TestLoadModels(unittest.TestCase):
    def setUp(self):
        self.sys_path_save = sys.path
        self.cwd_save = os.getcwd()

        config = os.path.join(test_path, "test_config.yaml")
        from xosconfig import Config

        Config.clear()
        Config.init(config, "synchronizer-config-schema.yaml")

        from xossynchronizer import loadmodels
        from xossynchronizer.loadmodels import ModelLoadClient

        self.loadmodels = loadmodels

        self.api = MagicMock()
        self.api.dynamicload_pb2.LoadModelsRequest = MockLoadModelsRequest
        self.loader = ModelLoadClient(self.api)

    def tearDown(self):
        sys.path = self.sys_path_save
        os.chdir(self.cwd_save)

    def test_upload_models(self):
        dir_map = {
            "models_dir": ["models.xproto", "models.py"],
            "models_dir/convenience": ["convenience1.py"],
            "models_dir/../migrations": ["migration1.py", "migration2.py"],
        }

        file_map = {
            "models_dir/models.xproto": u"some xproto",
            "models_dir/models.py": u"print `python models file`",
            "models_dir/convenience": u"directory",
            "models_dir/convenience/convenience1.py": u"print `python convenience file`",
            "models_dir/../migrations": u"directory",
            "models_dir/../migrations/migration1.py": u"print `first migration`",
            "models_dir/../migrations/migration2.py": u"print `second migration`",
        }

        orig_open = builtins.open
        with patch(
            "os.listdir", side_effect=functools.partial(mock_listdir, dir_map)
        ), patch(
            "os.path.exists", side_effect=functools.partial(mock_exists, file_map)
        ), patch(
            py_builtins + ".open",
            side_effect=functools.partial(mock_open, orig_open, file_map),
        ):
            self.loader.upload_models("myservice", "models_dir", "1.2")

            request = self.api.dynamicload.LoadModels.call_args[0][0]
            self.assertEqual(request.name, "myservice")
            self.assertEqual(request.version, "1.2")

            self.assertEqual(len(request.xprotos.items), 1)
            self.assertEqual(request.xprotos.items[0].filename, "models.xproto")
            self.assertEqual(request.xprotos.items[0].contents, u"some xproto")

            self.assertEqual(len(request.decls.items), 1)
            self.assertEqual(request.decls.items[0].filename, "models.py")
            self.assertEqual(
                request.decls.items[0].contents, u"print `python models file`"
            )

            self.assertEqual(len(request.convenience_methods.items), 1)
            self.assertEqual(
                request.convenience_methods.items[0].filename, "convenience1.py"
            )
            self.assertEqual(
                request.convenience_methods.items[0].contents,
                u"print `python convenience file`",
            )

            self.assertEqual(len(request.migrations.items), 2)
            self.assertEqual(request.migrations.items[0].filename, "migration1.py")
            self.assertEqual(
                request.migrations.items[0].contents, u"print `first migration`"
            )
            self.assertEqual(request.migrations.items[1].filename, "migration2.py")
            self.assertEqual(
                request.migrations.items[1].contents, u"print `second migration`"
            )


if __name__ == "__main__":
    unittest.main()
