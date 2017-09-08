#!/usr/bin/env bash

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

BASEDIR=$(pwd)
VENVDIR=venv-xosdocs

# create venv if it's not yet there
if [ ! -d "$BASEDIR/$VENVDIR" ]; then
    echo "Setting up virtualenv for XOS Swagger Docs"
    virtualenv -q $BASEDIR/$VENVDIR --no-site-packages
    pip install --upgrade pip
    echo "Virtualenv created."
fi

# activate the virtual env
if [ ! $VIRTUAL_ENV ]; then
    source $BASEDIR/$VENVDIR/bin/activate
    echo "Virtualenv activated."
fi

# install pip packages
pip install -e $BASEDIR/$VENVDIR/../../lib/xos-genx
pip install plyxproto jinja2 pattern astunparse pyyaml

