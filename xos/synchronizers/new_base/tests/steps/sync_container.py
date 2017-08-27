
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


import hashlib
import os
import socket
import sys
import base64
import time
from synchronizers.new_base.SyncInstanceUsingAnsible import SyncInstanceUsingAnsible
from synchronizers.new_base.syncstep import DeferredException
from synchronizers.new_base.ansible_helper import run_template_ssh
from mock_modelaccessor import *
from synchronizers.new_base.syncstep import SyncStep

# hpclibrary will be in steps/..
parentdir = os.path.join(os.path.dirname(__file__),"..")
sys.path.insert(0, parentdir)

class SyncContainer(SyncInstanceUsingAnsible):
    provides=[Instance]
    observes=Instance
    template_name = "sync_container.yaml"

    def __init__(self, *args, **kwargs):
        super(SyncContainer, self).__init__(*args, **kwargs)

    def fetch_pending(self, deletion=False):
        i = Instance()
        i.name = "Spectacular Sponge"
        j = Instance()
        j.name = "Spontaneous Tent"
        k = Instance()
        k.name = "Embarrassed Cat"

        objs = [i,j,k]
        return objs

    def sync_record(self, o):
        pass

    def delete_record(self, o):
        pass
