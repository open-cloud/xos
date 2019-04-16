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

""" BackupHandler

    This file contains code to interface with various backends (django, postgres, etc) for creating
    and restoring backups. Backend-specific code is isolated here to make it easier to port and easier
    to use.
"""

import os

from xosconfig import Config
from multistructlog import create_logger

# TODO(smbaker): Write a django BackupHandler that uses dumpdata and loaddata


class BackupHandler_postgres(object):
    """ This backuphandler uses postgres pg_dump and psql """
    def __init__(self):
        self.db_name = Config().get("database.name")
        self.db_username = Config().get("database.username")
        self.db_password = Config().get("database.password")
        self.db_host = "xos-db"
        self.db_port = "5432"
        self.log = create_logger(Config().get("logging"))

    def backup(self, filename):
        cmd = "PGPASSWORD=\"%s\" pg_dump -h %s -p %s -U %s -c %s > %s" % \
            (self.db_password, self.db_host, self.db_port, self.db_username, self.db_name, filename)
        self.log.info("Shell execute: %s" % cmd)
        result = os.system(cmd)
        self.log.info("Shell result", result=result)
        if result != 0:
            raise Exception("pgdump failed")

    def restore(self, filename):
        cmd = "PGPASSWORD=\"%s\" psql -h %s -p %s -U %s %s < %s > /dev/null" % \
            (self.db_password, self.db_host, self.db_port, self.db_username, self.db_name, filename)
        self.log.info("Shell execute: %s" % cmd)
        result = os.system(cmd)
        self.log.info("Shell result", result=result)
        if result != 0:
            raise Exception("psql failed")


BackupHandler = BackupHandler_postgres
