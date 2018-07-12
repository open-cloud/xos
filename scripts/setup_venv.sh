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

set -e -o pipefail

WORKSPACE=${WORKSPACE:-.}
XOS_DIR=${XOS_DIR:-.}
PIP_REQS=${PIP_REQS:-${XOS_DIR}/scripts/xos_dev_reqs.txt}
VENVDIR="${WORKSPACE}/venv-xos"

# create venv if it's not yet there
if [ ! -x "${VENVDIR}/bin/activate" ]; then
  echo "Setting up dev/test virtualenv in ${VENVDIR} for XOS"
  virtualenv -q "${VENVDIR}" --no-site-packages
  echo "Virtualenv created."
fi

echo "Installing python requirements in virtualenv with pip"
source "${VENVDIR}/bin/activate"
pip install --upgrade pip
pip install -r "$PIP_REQS"

pushd "$XOS_DIR/lib/xos-util"
python setup.py install
echo "xos-util Installed"
popd

pushd "$XOS_DIR/lib/xos-config"
python setup.py install
echo "xos-config Installed"
popd

pushd "$XOS_DIR//lib/xos-genx"
python setup.py install
echo "xos-genx Installed"
popd

pushd "$XOS_DIR/xos/xos_client"
make
echo "xos-client Installed"
popd

echo "XOS dev/test virtualenv created. Run 'source ${VENVDIR}/bin/activate'."
