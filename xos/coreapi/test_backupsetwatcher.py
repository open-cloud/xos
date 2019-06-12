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

import functools
import json
import os
import sys
import unittest
from mock import MagicMock, Mock, patch
from pyfakefs import fake_filesystem_unittest
from io import open
from xosconfig import Config

XOS_DIR = os.path.join(os.path.dirname(__file__), "..")

def make_model(vars_dict, var_name, **kwargs):
    """ Helper function to mock creating objects. Creates a MagicMock with the
        kwargs, and also saves the variable into a dictionary where it can
        easily be inspected.
    """
    name = kwargs.pop("name", None)
    newmodel = MagicMock(**kwargs)
    if name:
        # Can't pass "name" in as an arg to MagicMock
        newmodel.name = name
    vars_dict[var_name] = newmodel
    return newmodel


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

        # needed because decorators.py imports xos.exceptions
        self.sys_path_save = sys.path
        sys.path = [XOS_DIR] + sys.path

        import decorators
        decorators.disable_check_db_connection_decorator = True

        import backupsetwatcher
        self.backupsetwatcher = backupsetwatcher

        self.setUpPyfakefs()

        self.server = MockServer()
        self.watcher = backupsetwatcher.BackupSetWatcherThread(self.server)

    def tearDown(self):
        sys.path = self.sys_path_save

    def test_init_request_dir(self):
        self.assertFalse(os.path.exists(self.watcher.backup_request_dir))

        # Should create the directory
        self.watcher.init_request_dir()
        self.assertTrue(os.path.exists(self.watcher.backup_request_dir))

        # Should remove any existing files
        fn = os.path.join(self.watcher.backup_request_dir, "foo")
        open(fn, "w").write("foo")
        self.watcher.init_request_dir()
        self.assertFalse(os.path.exists(fn))

    def test_process_response_create_noexist(self):
        file_details = {"checksum": "1234"}
        response = {"file_details": file_details}

        self.backupsetwatcher.BackupOperation.objects.filter.return_value = []

        with self.assertRaises(self.backupsetwatcher.BackupDoesNotExist):
            self.watcher.process_response_create(uuid="one", operation="create", status="created", response=response)

    def test_process_response_create(self):
        file_details = {"checksum": "1234"}
        response = {"file_details": file_details,
                    "effective_date": "today"}

        file = MagicMock()
        op = MagicMock(file=file)

        self.backupsetwatcher.BackupOperation.objects.filter.return_value = [op]

        self.watcher.process_response_create(uuid="one", operation="create", status="created", response=response)

        self.assertEqual(op.file.checksum, "1234")
        op.file.save.assert_called()

        self.assertEqual(op.status, "created")
        self.assertEqual(op.error_msg, "")
        self.assertEqual(op.effective_date, "today")
        op.save.assert_called()

    def test_process_response_restore_noexist(self):
        file_details = {"id": 7,
                        "name": "mybackup",
                        "uri": "file:///mybackup",
                        "checksum": "1234",
                        "backend_filename": "/mybackup"}
        response = {"file_details": file_details,
                    "effective_date": "today"}

        mockvars = {}

        self.backupsetwatcher.BackupFile.objects.filter.return_value = []
        self.backupsetwatcher.BackupFile.side_effect = functools.partial(make_model, mockvars, "newfile")

        self.backupsetwatcher.BackupOperation.objects.filter.return_value = []
        self.backupsetwatcher.BackupOperation.side_effect = functools.partial(make_model, mockvars, "newop")

        self.watcher.process_response_restore(uuid="one", operation="restore", status="restored", response=response)

        newfile = mockvars["newfile"]
        self.assertEqual(newfile.name, "mybackup")
        self.assertEqual(newfile.uri, "file:///mybackup")
        self.assertEqual(newfile.checksum, "1234")
        self.assertEqual(newfile.backend_filename, "/mybackup")

        newop = mockvars["newop"]
        self.assertEqual(newop.operation, "restore")
        self.assertEqual(newop.file, newfile)
        self.assertEqual(newop.status, "restored")
        self.assertEqual(newop.error_msg, "")
        self.assertEqual(newop.effective_date, "today")
        newop.save.assert_called()

    def test_process_response_restore_exists(self):
        file_details = {}
        response = {"file_details": file_details,
                    "effective_date": "today"}

        file = MagicMock()
        op = MagicMock(file=file)

        self.backupsetwatcher.BackupOperation.objects.filter.return_value = [op]

        self.watcher.process_response_restore(uuid="one", operation="restore", status="restored", response=response)

        self.assertEqual(op.status, "restored")
        self.assertEqual(op.error_msg, "")
        self.assertEqual(op.effective_date, "today")
        op.save.assert_called()

    def test_process_response_dir_create(self):
        # BackupSetWatcher's __init__ method will have already called process_response_dir
        # This means the backup_response_dir will be already created.

        self.assertTrue(os.path.exists(self.watcher.backup_response_dir))

        file_details = {"backend_filename": "/mybackup"}
        resp = {"uuid": "seven", "operation": "create", "status": "created", "file_details": file_details}
        resp_fn = os.path.join(self.watcher.backup_response_dir, "response")

        with open(resp_fn, "w") as resp_f:
            resp_f.write(json.dumps(resp))

        with patch.object(self.watcher, "process_response_create") as process_response_create, \
                patch.object(self.watcher, "process_response_restore") as process_response_restore:
            self.watcher.process_response_dir()

            process_response_create.assert_called()
            process_response_restore.assert_not_called()

    def test_process_response_dir_restore(self):
        # BackupSetWatcher's __init__ method will have already called process_response_dir
        # This means the backup_response_dir will be already created.

        self.assertTrue(os.path.exists(self.watcher.backup_response_dir))

        file_details = {"backend_filename": "/mybackup"}
        resp = {"uuid": "seven", "operation": "restore", "status": "restored", "file_details": file_details}
        resp_fn = os.path.join(self.watcher.backup_response_dir, "response")

        with open(resp_fn, "w") as resp_f:
            resp_f.write(json.dumps(resp))

        with patch.object(self.watcher, "process_response_create") as process_response_create, \
                patch.object(self.watcher, "process_response_restore") as process_response_restore:
            self.watcher.process_response_dir()

            process_response_create.assert_not_called()
            process_response_restore.assert_called()

    def test_save_request(self):
        file = Mock(id=7,
                    uri="file:///mybackup",
                    checksum="1234",
                    backend_filename="/mybackup")
        file.name = "mybackup",

        request = Mock(id=3,
                       uuid="three",
                       file=file,
                       operation="create")

        os.makedirs(self.watcher.backup_request_dir)

        self.watcher.save_request(request)

        req_fn = os.path.join(self.watcher.backup_request_dir, "request")
        data = json.loads(open(req_fn).read())

        expected_data = {u'operation': u'create',
                         u'id': 3,
                         u'uuid': "three",
                         u'file_details': {u'backend_filename': u'/mybackup',
                                           u'checksum': u'1234',
                                           u'uri': u'file:///mybackup',
                                           u'name': [u'mybackup'],
                                           u'id': 7}}

        self.assertDictEqual(data, expected_data)

    def test_run_once_create(self):
        file = Mock(id=7,
                    uri="file:///var/run/xos/backup/local/mybackup",
                    checksum="1234")
        file.name = "mybackup",

        request = Mock(id=3,
                       uuid="three",
                       file=file,
                       component="xos",
                       operation="create",
                       status=None)

        self.backupsetwatcher.BackupOperation.objects.filter.return_value = [request]

        with patch.object(self.watcher, "save_request") as save_request, \
                patch.object(self.server, "delayed_shutdown") as delayed_shutdown:
            self.watcher.run_once()

            self.assertEqual(save_request.call_count, 1)
            saved_op = save_request.call_args[0][0]

            self.assertEqual(request, saved_op)
            self.assertEqual(saved_op.status, "inprogress")
            self.assertEqual(saved_op.file.backend_filename, "/var/run/xos/backup/local/mybackup")
            self.assertTrue(self.watcher.exiting)

            delayed_shutdown.assert_called()

    def test_run_once_restore(self):
        file = Mock(id=7,
                    uri="file:///var/run/xos/backup/local/mybackup",
                    checksum="1234")
        file.name = "mybackup",

        request = Mock(id=3,
                       uuid="three",
                       file=file,
                       component="xos",
                       operation="restore",
                       status=None)

        self.backupsetwatcher.BackupOperation.objects.filter.return_value = [request]

        with patch.object(self.watcher, "save_request") as save_request, \
                patch.object(self.server, "delayed_shutdown") as delayed_shutdown:
            self.watcher.run_once()

            self.assertEqual(save_request.call_count, 1)
            saved_op = save_request.call_args[0][0]

            self.assertEqual(request, saved_op)
            self.assertEqual(saved_op.status, "inprogress")
            self.assertEqual(saved_op.file.backend_filename, "/var/run/xos/backup/local/mybackup")
            self.assertTrue(self.watcher.exiting)

            delayed_shutdown.assert_called()

    def test_run_once_not_xos(self):
        file = Mock(id=7,
                    uri="file:///var/run/xos/backup/local/mybackup",
                    checksum="1234")
        file.name = "mybackup",

        request = Mock(id=3,
                       uuid="three",
                       file=file,
                       component="somethingelse",
                       operation="create",
                       status=None)

        self.backupsetwatcher.BackupOperation.objects.filter.return_value = [request]

        with patch.object(self.watcher, "save_request") as save_request, \
                patch.object(self.server, "delayed_shutdown") as delayed_shutdown:
            self.watcher.run_once()

            save_request.assert_not_called()
            delayed_shutdown.assert_not_called()


def main():
    unittest.main()


if __name__ == "__main__":
    main()
