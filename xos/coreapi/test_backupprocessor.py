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
import unittest
from mock import MagicMock, patch, ANY, call
from pyfakefs import fake_filesystem_unittest
from io import open

from __builtin__ import True as builtin_True, False as builtin_False

from xosconfig import Config


def mock_make_backup(fn):
    with open(fn, "w") as backup_f:
        backup_f.write("stuff")


class TestBackupProcessor(fake_filesystem_unittest.TestCase):
    def setUp(self):
        config = os.path.abspath(
            os.path.dirname(os.path.realpath(__file__)) + "/test_config.yaml"
        )
        Config.clear()  # in case left unclean by a previous test case
        Config.init(config)

        import backupprocessor
        self.backupprocessor = backupprocessor

        self.setUpPyfakefs()

        self.processor = backupprocessor.BackupProcessor()
        self.mock_backuphandler = MagicMock(backup=MagicMock(), restore=MagicMock())

    def tearDown(self):
        pass

    def test_compute_checksum(self):
        with open("/tmp/somefile", "w") as somefile:
            somefile.write("test")
            self.assertEqual(self.processor.compute_checksum("/tmp/somefile"),
                             "sha1:da39a3ee5e6b4b0d3255bfef95601890afd80709")

    def test_try_models(self):
        with patch("os.system") as os_system:
            os_system.return_value = 0
            self.processor.try_models()

            os_system.assert_called_with("python try_models.py")

    def test_emergency_rollback(self):
        with patch.object(self.processor, "get_backuphandler") as get_backuphandler:
            get_backuphandler.return_value = self.mock_backuphandler

            self.processor.emergency_rollback("/tmp/foo")
            self.mock_backuphandler.restore.assert_called_with("/tmp/foo")

    def init_request(self, operation):
        os.makedirs(self.processor.backup_request_dir)

        request_fn = "request"
        request_pathname = os.path.join(self.processor.backup_request_dir, request_fn)
        backend_filename = os.path.join(self.processor.backup_file_dir, "mybackup")
        file_details = {"id": 7,
                        "name": "mybackup",
                        "uri": "file://" + backend_filename,
                        "backend_filename": backend_filename}
        req = {"id": 3,
               "uuid": "three",
               "operation": operation,
               "file_details": file_details,
               "request_fn": request_fn,
               "request_pathname": request_pathname}

        with open(request_pathname, "w") as req_fn:
            req_fn.write(json.dumps(req))

        return req

    def test_finalize_response(self):
        os.makedirs(self.processor.backup_response_dir)

        req = self.init_request("create")
        response_fn = os.path.join(self.processor.backup_response_dir, "request_response")

        resp = {}

        self.processor.finalize_response(req, resp, "created", checksum="1234")

        self.assertTrue(os.path.exists(response_fn))
        data = json.loads(open(response_fn).read())

        expected_data = {u'status': u'created',
                         u'effective_date': ANY,
                         u'operation': u'create',
                         u'id': 3,
                         u'uuid': u'three',
                         u'file_details': {u'backend_filename':
                                           u'/var/run/xos/backup/local/mybackup',
                                           u'checksum': u'1234',
                                           u'uri': u'file:///var/run/xos/backup/local/mybackup',
                                           u'name': u'mybackup',
                                           u'id': 7}}
        self.assertDictEqual(data, expected_data)

    def test_handle_backup_request(self):
        os.makedirs(self.processor.backup_response_dir)

        req = self.init_request("create")

        with patch.object(self.processor, "get_backuphandler") as get_backuphandler:
            get_backuphandler.return_value = self.mock_backuphandler

            self.mock_backuphandler.backup.side_effect = mock_make_backup

            self.processor.handle_backup_request(req)

            self.mock_backuphandler.backup.assert_called_with("/var/run/xos/backup/local/mybackup")

            response_fn = os.path.join(self.processor.backup_response_dir, "request_response")
            data = json.loads(open(response_fn).read())

            expected_data = {u'status': u'created',
                             u'effective_date': ANY,
                             u'operation': u'create',
                             u'id': 3,
                             u'uuid': u'three',
                             u'file_details': {u'backend_filename': u'/var/run/xos/backup/local/mybackup',
                                               u'checksum': u'sha1:5eee38381388b6f30efdd5c5c6f067dbf32c0bb3',
                                               u'uri': u'file:///var/run/xos/backup/local/mybackup',
                                               u'name': u'mybackup',
                                               u'id': 7}}
            self.assertDictEqual(data, expected_data)

    def test_handle_restore_request(self):
        os.makedirs(self.processor.backup_response_dir)
        os.makedirs(self.processor.backup_file_dir)

        req = self.init_request("restore")

        print req["file_details"]["backend_filename"]
        with open(req["file_details"]["backend_filename"], "w") as backup_file:
            backup_file.write("stuff")

        with patch.object(self.processor, "get_backuphandler") as get_backuphandler, \
                patch.object(self.processor, "try_models") as try_models:
            get_backuphandler.return_value = self.mock_backuphandler
            try_models.return_value = builtin_True

            self.processor.handle_restore_request(req)

            self.mock_backuphandler.backup.assert_called_with("/var/run/xos/backup/local/emergency_rollback")
            self.mock_backuphandler.restore.assert_called_with("/var/run/xos/backup/local/mybackup")

            response_fn = os.path.join(self.processor.backup_response_dir, "request_response")
            data = json.loads(open(response_fn).read())

            expected_data = {u'status': u'restored',
                             u'effective_date': ANY,
                             u'operation': u'restore',
                             u'id': 3,
                             u'uuid': u'three',
                             u'file_details': {u'backend_filename': u'/var/run/xos/backup/local/mybackup',
                                               u'uri': u'file:///var/run/xos/backup/local/mybackup',
                                               u'name': u'mybackup',
                                               u'id': 7}}
            self.assertDictEqual(data, expected_data)

    def test_handle_restore_request_fail_try(self):
        """ Fails the restore operation during try_models, ensures that rollback was performed """

        os.makedirs(self.processor.backup_response_dir)
        os.makedirs(self.processor.backup_file_dir)

        req = self.init_request("restore")

        print req["file_details"]["backend_filename"]
        with open(req["file_details"]["backend_filename"], "w") as backup_file:
            backup_file.write("stuff")

        with patch.object(self.processor, "get_backuphandler") as get_backuphandler, \
                patch.object(self.processor, "try_models") as try_models:
            get_backuphandler.return_value = self.mock_backuphandler
            try_models.return_value = builtin_False

            self.processor.handle_restore_request(req)

            self.mock_backuphandler.backup.assert_called_with("/var/run/xos/backup/local/emergency_rollback")

            self.assertEqual(self.mock_backuphandler.restore.mock_calls,
                             [call("/var/run/xos/backup/local/mybackup"),
                              call("/var/run/xos/backup/local/emergency_rollback")])

            response_fn = os.path.join(self.processor.backup_response_dir, "request_response")
            data = json.loads(open(response_fn).read())

            expected_data = {u'status': u'failed',
                             u'error_msg': u'Try_models failed, emergency rollback performed',
                             u'effective_date': ANY,
                             u'operation': u'restore',
                             u'id': 3,
                             u'uuid': u'three',
                             u'file_details': {u'backend_filename': u'/var/run/xos/backup/local/mybackup',
                                               u'uri': u'file:///var/run/xos/backup/local/mybackup',
                                               u'name': u'mybackup',
                                               u'id': 7}}
            self.assertDictEqual(data, expected_data)

    def test_run_create(self):
        req = self.init_request("create")

        with patch.object(self.processor, "handle_backup_request") as handle_backup_request:
            self.processor.run()

            handle_backup_request.assert_called()

            handled_req = handle_backup_request.call_args[0][0]

            self.assertDictEqual(handled_req, req)

    def test_run_restore(self):
        req = self.init_request("restore")

        with patch.object(self.processor, "handle_restore_request") as handle_restore_request:
            self.processor.run()

            handle_restore_request.assert_called()

            handled_req = handle_restore_request.call_args[0][0]

            self.assertDictEqual(handled_req, req)

    def test_run_not_json(self):
        os.makedirs(self.processor.backup_request_dir)
        with open(os.path.join(self.processor.backup_request_dir, "request"), "w") as req_f:
            req_f.write("this is not json")

        with patch.object(self.processor, "handle_restore_request") as handle_restore_request, \
                patch.object(self.processor, "handle_backup_request") as handle_backup_request:
            self.processor.run()

            handle_restore_request.assert_not_called()
            handle_backup_request.assert_not_called()

    def test_run_not_understandable(self):
        os.makedirs(self.processor.backup_request_dir)
        request = {"somekey": "somevalue"}
        with open(os.path.join(self.processor.backup_request_dir, "request"), "w") as req_f:
            req_f.write(json.dumps(request))

        with patch.object(self.processor, "handle_restore_request") as handle_restore_request, \
                patch.object(self.processor, "handle_backup_request") as handle_backup_request:
            self.processor.run()

            handle_restore_request.assert_not_called()
            handle_backup_request.assert_not_called()


def main():
    unittest.main()


if __name__ == "__main__":
    main()
