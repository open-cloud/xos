#!/usr/bin/env python

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

from __future__ import absolute_import, print_function

import requests
import sys


def matches(test, item):
    if ">=" in test:
        delim = ">="
    elif ">" in test:
        delim = ">"
    elif "=" in test:
        delim = "="
    (name, value) = test.split(delim, 1)
    if value.startswith("@"):
        value = item[value[1:]]

    if delim == ">":
        if float(item[name]) > float(value):
            return True

    if delim == ">=":
        if float(item[name]) >= float(value):
            return True

    if delim == "=":
        if str(item[name]) == str(value):
            return True
    return False


def main():
    url = sys.argv[1]
    tests = sys.argv[2:]

    r = requests.get(url, auth=("admin@opencord.org", "letmein"))
    for item in r.json()["items"]:
        okay = True
        for test in tests:
            if not matches(test, item):
                okay = False
        if okay:
            print("matched")
            sys.exit(0)

    print("Not Matched")
    sys.exit(-1)


if __name__ == "__main__":
    main()
