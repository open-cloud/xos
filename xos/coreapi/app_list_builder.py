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


def makedirs_if_noexist(pathname):
    if not os.path.exists(pathname):
        os.makedirs(pathname)


class AppListBuilder(object):
    def __init__(self):
        self.app_metadata_dir = "/opt/xos/xos"
        self.services_dest_dir = "/opt/xos/services"
        self.service_manifests_dir = "/opt/xos/dynamic_services/manifests"

    def load_manifests(self):
        """ Load the manifests that were saved from LoadModels() calls """

        if not os.path.exists(self.service_manifests_dir):
            # No manifests dir means no services have been dynamically loaded yet
            return {}

        manifests = {}
        for fn in os.listdir(self.service_manifests_dir):
            manifest_fn = os.path.join(self.service_manifests_dir, fn)
            manifest = json.loads(open(manifest_fn).read())
            if not "name" in manifest:
                # sanity check
                continue
            manifests[manifest["name"]] = manifest

        return manifests

    def generate_app_lists(self):
        app_names = []
        automigrate_app_names = []

        manifests = self.load_manifests()
        for manifest in manifests.values():
            # We're only interested in apps that contain models
            if manifest.get("xprotos"):
                app_names.append(manifest["name"])

                # Only apps that do not already have migration scripts will get automigrated
                # TODO(smbaker): Eventually all apps will have migration scripts. Drop this when that happens.
                if not manifest.get("migrations"):
                    automigrate_app_names.append(manifest["name"])

        # Generate the auto-migration list
        mig_list_fn = os.path.join(self.app_metadata_dir, "xosbuilder_migration_list")
        makedirs_if_noexist(os.path.dirname(mig_list_fn))
        file(mig_list_fn, "w").write("\n".join(automigrate_app_names) + "\n")

        # Generate the app list
        app_list_fn = os.path.join(self.app_metadata_dir, "xosbuilder_app_list")
        makedirs_if_noexist(os.path.dirname(app_list_fn))
        file(app_list_fn, "w").write(
            "\n".join(["services.%s" % x for x in app_names]) + "\n"
        )


if __name__ == "__main__":
    AppListBuilder().generate_app_lists()
