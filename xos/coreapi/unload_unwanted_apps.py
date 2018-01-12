
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

import json
import os
import shutil

class AppUnloader(object):
    def __init__(self):
        self.manifests_dir = "/opt/xos/dynamic_services/manifests"

    def unload_all_eligible(self):
        if not os.path.exists(self.manifests_dir):
            # nothing to do...
            return

        for fn in os.listdir(self.manifests_dir):
            if fn.endswith(".json"):
                manifest_fn = os.path.join(self.manifests_dir, fn)
                manifest = json.loads(open(manifest_fn).read())
                if manifest.get("state") == "unload":
                    self.unload_service(manifest)

    def unload_service(self, manifest):
        if not os.path.exists(manifest["dest_dir"]):
            # service is deleted -- nothing to do
            return

        os.system("cd /opt/xos; python ./manage.py migrate %s zero" % manifest["name"])

        # be paranoid about calling rmtree
        assert(os.path.abspath(manifest["dest_dir"]).startswith("/opt/xos"))

        shutil.rmtree(manifest["dest_dir"])

if __name__ == "__main__":
    AppUnloader().unload_all_eligible()
