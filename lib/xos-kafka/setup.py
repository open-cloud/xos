#!/usr/bin/env python

# Copyright 2018-present Open Networking Foundation
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


def readme():
    with open('README.rst') as f:
        return f.read()


setup_with_auto_version(
    name='xoskafka',
    version=__version__,
    description='Wrapper around kafka for XOS',
    long_description=readme(),
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
    ],
    author='Zack Williams',
    author_email='zdw@opennetworking.org',
    packages=['xoskafka'],
    license='Apache v2',
    install_requires=[
        'confluent-kafka>=0.11.5',
        'xosconfig>=2.1.0',
        'multistructlog>=1.5',
        ],
    include_package_data=True,
    zip_safe=False,
    )
