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

# setup_venv_lite.sh
# sets up a python virtualenv for testing and service development

set -eu -o pipefail

BASEDIR=$(pwd)
REQUIREMENTS=$BASEDIR/scripts/xos_reqs_lite.txt
VENVDIR=venv-xos-lite

# create venv if it's not yet there
if [ ! -x "$BASEDIR/$VENVDIR/bin/activate" ]; then
  echo "Setting up virtualenv ${BASEDIR}/${VENVDIR} for XOS"
  virtualenv -q "$BASEDIR/$VENVDIR" --no-site-packages
  pip install --upgrade pip
  echo "Virtualenv created."
fi

set +u
# activate the virtual env
if [ ! -x "$VIRTUAL_ENV" ]; then
  source "$BASEDIR/$VENVDIR/bin/activate"
  echo "Virtualenv activated."
fi

pip install -r "$REQUIREMENTS"
cd "$BASEDIR/lib/xos-config"; python setup.py install
cd "$BASEDIR/lib/xos-genx"; python setup.py install
cd "$BASEDIR/lib/xos-util"; python setup.py install

