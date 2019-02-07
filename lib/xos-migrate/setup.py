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

try:
    from xosutil.autoversion_setup import setup_with_auto_version as setup
except ImportError:
    # xosutil is not installed. Expect this to happen when we build an egg, in which case xosgenx.version will
    # automatically have the right version.
    from setuptools import setup

from xosgenx.version import __version__

setup(
    name="XosMigrate",
    version=__version__,
    description="XOS Migrations Toolkit",
    author="Matteo Scandolo",
    author_email="teo@opennetworking.org",
    packages=["xosmigrate"],
    scripts=["bin/xos-migrate"],
    include_package_data=True,
    # TODO add all deps to the install_requires section
    install_requires=[],
)
