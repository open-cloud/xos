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

import socket
import struct
from uuid import uuid4

from xos.exceptions import *
from backupoperation_decl import *


class BackupOperation(BackupOperation_decl):
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid4()
        super(BackupOperation, self).save(*args, **kwargs)
