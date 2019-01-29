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


from xosutil.autoversion_setup import setup_with_auto_version
from xosutil.version import __version__

setup_with_auto_version(
    name="XosSynchronizer",
    version=__version__,
    description="XOS Synchronizer Framework",
    author="Scott Baker",
    author_email="scottb@opennetworking.org",
    packages=[
        "xossynchronizer",
        "xossynchronizer.steps",
        "xossynchronizer.event_steps",
        "xossynchronizer.pull_steps",
        "xossynchronizer.model_policies"],
    include_package_data=True,
    test_suite='nose2.collector.collector',
    tests_require=['nose2'],
    install_requires=["xosconfig>=2.1.35",],
)
