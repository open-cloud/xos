
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


import traceback
import json

from xosconfig import Config
from multistructlog import create_logger

log = create_logger(Config().get('logging'))


def update_diag(diag_class, loop_end=None, loop_start=None, syncrecord_start=None, sync_start=None,
                backend_status=None, backend_code=0):
    observer_name = Config.get("name")

    try:
        diag = diag_class.objects.filter(name=observer_name).first()
        if (not diag):
            if hasattr(diag_class.objects, "new"):
                # api style
                diag = diag_class.objects.new(name=observer_name)
            else:
                # django style
                diag = diag_class(name=observer_name)
        br_str = diag.backend_register
        if br_str:
            br = json.loads(br_str)
        else:
            br = {}
        if loop_end:
            br['last_run'] = loop_end
        if loop_end and loop_start:
            br['last_duration'] = loop_end - loop_start
        if syncrecord_start:
            br['last_syncrecord_start'] = syncrecord_start
        if sync_start:
            br['last_synchronizer_start'] = sync_start
        if backend_status:
            diag.backend_status = backend_status
        diag.backend_register = json.dumps(br)
        diag.save()
    except:
        log.exception("Exception in update_diag")
        traceback.print_exc()
