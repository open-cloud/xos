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

import os
import pdb
import sys
import unittest
from mock import MagicMock, Mock
from pyfakefs import fake_filesystem_unittest
from io import open

from xosconfig import Config


class MockServer(object):
    def __init__(self):
        super(MockServer, self).__init__()

    def delayed_shutdown(self, seconds):
        pass


class TestBackupWatcher(fake_filesystem_unittest.TestCase):
    def setUp(self):
        config = os.path.abspath(
            os.path.dirname(os.path.realpath(__file__)) + "/test_config.yaml"
        )
        Config.clear()  # in case left unclean by a previous test case
        Config.init(config)

        self.mock_backup_operation = MagicMock()
        self.mock_backup_file = MagicMock()

        sys.modules["core"] = Mock()
        sys.modules["core.models"] = Mock(BackupOperation=self.mock_backup_operation,
                                          BackupFile=self.mock_backup_file)

        import backupsetwatcher
        self.backupsetwatcher = backupsetwatcher

        self.setUpPyfakefs()

        self.server = MockServer()
        self.watcher = backupsetwatcher.BackupSetWatcherThread(self.server)

    def tearDown(self):
        pass

    def test_init_request_dir(self):
        self.assertFalse(os.path.exists(self.watcher.backup_request_dir))

        # Should create the directory
        self.watcher.init_request_dir()
        self.assertTrue(os.path.exists(self.watcher.backup_request_dir))

        # Shoudl remove any existing files
        fn = os.path.join(self.watcher.backup_request_dir, "foo")
        open(fn, "w").write("foo")
        self.watcher.init_request_dir()
        self.assertFalse(os.path.exists(fn))

    def test_process_response_create_noexist(self):
        file_details = {"checksum": "1234"}
        response = {"file_details": file_details}

        self.backupsetwatcher.BackupOperation.objects.filter.return_value = []

        with self.assertRaises(self.backupsetwatcher.BackupDoesNotExist):
            self.watcher.process_response_create(id=1, operation="create", status="created", response=response)

    def test_process_response_create(self):
        file_details = {"checksum": "1234"}
        response = {"file_details": file_details}

        file = MagicMock()
        op = MagicMock(file=file)

        self.backupsetwatcher.BackupOperation.objects.filter.return_value = [op]

        self.watcher.process_response_create(id=1, operation="create", status="created", response=response)

        self.assertEqual(op.file.checksum, "1234")
        op.file.save.assert_called()

        self.assertEqual(op.status, "created")
        self.assertEqual(op.error_msg, "")
        op.save.assert_called()


def main():
    unittest.main()


if __name__ == "__main__":
    main()
