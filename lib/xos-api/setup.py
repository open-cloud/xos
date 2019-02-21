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
from setuptools.command.install import install

try:
    from xosutil.autoversion_setup import setup_with_auto_version as setup
except ImportError:
    # xosutil is not installed. Expect this to happen when we build an egg, in which case xosgenx.version will
    # automatically have the right version.
    from setuptools import setup

from xosapi.version import __version__


class InstallFixChameleonPermissions(install):
    # Chameleon requires these files have executable permission set,
    # but setup.py installs them without the execute bit.
    def run(self):
        install.run(self)
        for filepath in self.get_outputs():
            if filepath.endswith(
                "chameleon_client/protoc_plugins/gw_gen.py"
            ):
                os.chmod(filepath, 0o777)


setup_result = setup(
    name="xosapi",
    version=__version__,
    cmdclass={"install": InstallFixChameleonPermissions},
    description="XOS api client",
    packages=[
        "xosapi.chameleon_client",
        "xosapi.chameleon_client.protos",
        "xosapi.chameleon_client.protoc_plugins",
        "xosapi",
        "xosapi.convenience",
    ],
    scripts=["xossh"],
)
