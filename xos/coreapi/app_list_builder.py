
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

def makedirs_if_noexist(pathname):
    if not os.path.exists(pathname):
        os.makedirs(pathname)

class AppListBuilder(object):
    def __init__(self):
        self.app_metadata_dir = "/opt/xos/xos"
        self.services_dest_dir = "/opt/xos/services"

    def generate_app_lists(self):
        # TODO: Once static onboarding is no more, we will get these from the manifests rather than using listdir
        app_names = []
        for fn in os.listdir(self.services_dest_dir):
            service_dir = os.path.join(self.services_dest_dir, fn)
            if (not fn.startswith(".")) and os.path.isdir(service_dir):
                models_fn = os.path.join(service_dir, "models.py")
                if os.path.exists(models_fn):
                    app_names.append(fn)

        # Generate the migration list
        mig_list_fn = os.path.join(self.app_metadata_dir, "xosbuilder_migration_list")
        makedirs_if_noexist(os.path.dirname(mig_list_fn))
        file(mig_list_fn, "w").write("\n".join(app_names) + "\n")

        # Generate the app list
        app_list_fn = os.path.join(self.app_metadata_dir, "xosbuilder_app_list")
        makedirs_if_noexist(os.path.dirname(app_list_fn))
        file(app_list_fn, "w").write("\n".join(["services.%s" % x for x in app_names]) + "\n")

if __name__ == "__main__":
    AppListBuilder().generate_app_lists()
