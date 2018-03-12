
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

import psycopg2
import sys
import time
import traceback

from xosconfig import Config

Config.init()

def wait_for_database():
    while True:
        db_name = Config.get("database.name")
        db_user = Config.get("database.username")
        db_password = Config.get("database.password")
        db_host = "xos-db"  # TODO: this should be configurable
        db_port = 5432      # TODO: this should be configurable

        try:
            myConnection = psycopg2.connect(host = db_host, port = db_port,
                                            user = db_user, password = db_password)



            myConnection.close()

            # Exit on successful connection
            print "Database is available"
            return
        except:
            traceback.print_exc("Exception while connecting to db")
            time.sleep(1)

wait_for_database()
