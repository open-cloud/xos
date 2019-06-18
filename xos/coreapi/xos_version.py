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

import datetime
from django import VERSION as DJANGO_VERSION
import os
import sys
from xosconfig import Config
from multistructlog import create_logger

log = create_logger(Config().get("logging"))


def get_version_dict():
    """ Return built-time version information """
    res = {}
    try:
        res["version"] = open("/opt/xos/VERSION").readline().strip()
    except Exception:
        log.exception("Exception while determining build version")
        res["version"] = "unknown"

    try:
        res["gitCommit"] = open("/opt/xos/COMMIT").readline().strip()
        res["buildTime"] = datetime.datetime.utcfromtimestamp(
            os.stat("/opt/xos/COMMIT").st_ctime).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        log.exception("Exception while determining build information")
        res["buildDate"] = "unknown"
        res["gitCommit"] = "unknown"

    res["pythonVersion"] = sys.version.split("\n")[0].strip().split(" ")[0]
    res["os"] = os.uname()[0].lower()
    res["arch"] = os.uname()[4].lower()
    res["djangoVersion"] = ".".join([str(x) for x in DJANGO_VERSION])

    return res
