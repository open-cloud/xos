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

import re
import signal
import sys


def handler(signum, frame):
    print "Timed Out"
    sys.exit(-1)


signal.signal(signal.SIGALRM, handler)
signal.alarm(60)  # timeout in 60 seconds

waitlines = open(sys.argv[1]).readlines()
waitlines = [x.strip() for x in waitlines]

while True:
    if not waitlines:
        print("all lines matched")
        break
    line = sys.stdin.readline()
    line = line.strip()
    for pattern in waitlines[:]:
        if re.match(pattern, line):
            print("matched", pattern)
            waitlines.remove(pattern)
