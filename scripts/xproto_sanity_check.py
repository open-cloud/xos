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

import os
from xosgenx.generator import XOSProcessor, XOSProcessorArgs

# These assume a traditional CORD/SEBA hierarchy is checked out using `repo`

SCRIPT_DIR=os.path.dirname(os.path.realpath(__file__))
BASE_DIR=os.path.join(SCRIPT_DIR,"..","..","..")
SERVICES_DIR=os.path.join(BASE_DIR,"orchestration","xos-services")
CORE_XPROTO=os.path.join(BASE_DIR,"orchestration","xos","xos","core","models","core.xproto")
TARGET=os.path.join(BASE_DIR,"orchestration","xos","lib","xos-genx","xosgenx","targets","fieldlist.xtarget")

def get_all_xproto():
    xprotos=[]
    for service_name in os.listdir(SERVICES_DIR):
        if service_name.startswith("."):
            continue
        service_path = os.path.join(SERVICES_DIR, service_name)
        if not os.path.isdir(service_path):
            continue
        models_dir = os.path.join(service_path, "xos", "synchronizer", "models")
        if not os.path.isdir(models_dir):
            continue
        for xproto_name in os.listdir(models_dir):
            if xproto_name.startswith("."):
                continue
            if not xproto_name.endswith(".xproto"):
                continue
            xproto_pathname = os.path.join(models_dir, xproto_name)
            xprotos.append(xproto_pathname)
    return xprotos

xprotos = get_all_xproto() + [CORE_XPROTO]
args = XOSProcessorArgs(files=xprotos,
                        target=TARGET,
                        verbosity=1
                        )
output = XOSProcessor.process(args)
