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
import unittest
from mock import patch

from xosconfig import Config


class TestBackupHandler(unittest.TestCase):
    def setUp(self):
        config = os.path.abspath(
            os.path.dirname(os.path.realpath(__file__)) + "/test_config.yaml"
        )
        Config.clear()  # in case left unclean by a previous test case
        Config.init(config)

        import backuphandler

        self.handler_postgres = backuphandler.BackupHandler_postgres()

    def tearDown(self):
        pass

    def test_postgres_init(self):
        self.assertEqual(self.handler_postgres.db_name, "xos")
        self.assertEqual(self.handler_postgres.db_username, "postgres")
        self.assertEqual(self.handler_postgres.db_password, "password")
        self.assertEqual(self.handler_postgres.db_host, "xos-db")
        self.assertEqual(self.handler_postgres.db_port, "5432")

    def test_postgres_backup(self):
        filename = "/tmp/foo"
        with patch("os.system") as os_system:
            os_system.return_value = 0
            self.handler_postgres.backup(filename)

            os_system.assert_called_with(
                'PGPASSWORD="password" pg_dump -h xos-db -p 5432 -U postgres -c xos > /tmp/foo')

    def test_postgres_backup_fail(self):
        filename = "/tmp/foo"
        with patch("os.system") as os_system:
            os_system.return_value = 1

            with self.assertRaises(Exception) as e:
                self.handler_postgres.backup(filename)

            self.assertEqual(str(e.exception), "pgdump failed")

    def test_postgres_restore(self):
        filename = "/tmp/foo"
        with patch("os.system") as os_system:
            os_system.return_value = 0
            self.handler_postgres.restore(filename)

            os_system.assert_called_with(
                'PGPASSWORD="password" psql -h xos-db -p 5432 -U postgres xos < /tmp/foo > /dev/null')

    def test_postgres_restore_fail(self):
        filename = "/tmp/foo"
        with patch("os.system") as os_system:
            os_system.return_value = 1

            with self.assertRaises(Exception) as e:
                self.handler_postgres.restore(filename)

            self.assertEqual(str(e.exception), "psql failed")


def main():
    unittest.main()


if __name__ == "__main__":
    main()
