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


def version():
    # Copy VERSION file of parent to module directory if not found
    if not os.path.exists("xosmigrate/VERSION"):
        copyfile("../../VERSION", "xosmigrate/VERSION")
    with open("xosmigrate/VERSION") as f:
        return f.read().strip()


def parse_requirements(filename):
    # parse a requirements.txt file, allowing for blank lines and comments
    requirements = []
    for line in open(filename):
        if line and not line.startswith("#"):
            requirements.append(line)
    return requirements


setup(
    name="xosmigrate",
    version=version(),
    description="XOS Migrations Toolkit",
    author="Matteo Scandolo",
    author_email="teo@opennetworking.org",
    classifiers=["License :: OSI Approved :: Apache Software License"],
    license="Apache v2",
    packages=["xosmigrate"],
    scripts=["bin/xos-migrate"],
    install_requires=parse_requirements("requirements.txt"),
    include_package_data=True,
)
