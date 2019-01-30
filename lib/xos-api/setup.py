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

from __future__ import absolute_import

import os
from shutil import copyfile

from setuptools import setup
from setuptools.command.install import install


def version():
    # Copy VERSION file of parent to module directory if not found
    if not os.path.exists("xosapi/VERSION"):
        copyfile("../../VERSION", "xosapi/VERSION")
    with open("xosapi/VERSION") as f:
        return f.read().strip()


def parse_requirements(filename):
    # parse a requirements.txt file, allowing for blank lines and comments
    requirements = []
    for line in open(filename):
        if line and not line.startswith("#"):
            requirements.append(line)
    return requirements


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
    version=version(),
    classifiers=["License :: OSI Approved :: Apache Software License"],
    license="Apache v2",
    cmdclass={"install": InstallFixChameleonPermissions},
    description="XOS API client",
    packages=[
        "xosapi.chameleon_client",
        "xosapi.chameleon_client.protos",
        "xosapi.chameleon_client.protoc_plugins",
        "xosapi",
        "xosapi.convenience",
    ],
    install_requires=parse_requirements("requirements.txt"),
    include_package_data=True,
    package_data={
        "xosapi.chameleon_client.protos": ["*.proto"],
        "xosapi.chameleon_client.protoc_plugins": ["*.desc"],
    },
    scripts=["xossh"],
)
