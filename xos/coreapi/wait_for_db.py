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
import argparse
import psycopg2
import time
import traceback

from xosconfig import Config

def wait_for_database(db_host, db_port, retry_interval):

    retry_count = 0

    db_user = Config.get("database.username")
    db_password = Config.get("database.password")

    while True:


        try:
            myConnection = psycopg2.connect(
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password,
                connect_timeout=5,
            )

            # Exit on successful connection
            print("Database is available")

            myConnection.close()
            return

        except psycopg2.OperationalError:
            # timeout reached, retrying
            retry_count += 1
            print("Timeout connecting to db, retrying (retry count: %d)" % retry_count)

        except BaseException:
            traceback.print_exc("Unknown exception while connecting to db")

        # sleep for the retry interval between retries
        time.sleep(float(retry_interval))


# parse argumens
parser = argparse.ArgumentParser()

parser.add_argument(
    "-c",
    "--config",
    dest="config",
    default="/opt/xos/xos_config.yaml",
    help="Location of XOS configuration file",
)

parser.add_argument(
    "-s",
    "--server",
    dest="db_host",
    default="xos-db",
    help="Database server hostname (DNS or IP) to connect to",
)

parser.add_argument(
    "-p",
    "--port",
    dest="db_port",
    default="5432",
    help="Database port on host to connect to",
)

parser.add_argument(
    "-r",
    "--retry-interval",
    dest="retry_interval",
    default="5",
    help="Interval between connection retries in seconds",
)

args = parser.parse_args()

Config.init(args.config)

wait_for_database(args.db_host, args.db_port, args.retry_interval)
