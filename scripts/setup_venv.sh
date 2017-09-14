#!/bin/bash

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
REQUIREMENTS=$BASEDIR/containers/xos/pip_requirements.txt
VENVDIR=venv-xos

echo $BASEDIR
echo $REQUIREMENTS
echo $VENVDIR

# create venv if it's not yet there
if [ ! -d "$BASEDIR/$VENVDIR" ]; then
   echo "Setting up virtualenv for XOS"
   virtualenv -q $BASEDIR/$VENVDIR --no-site-packages
   pip install --upgrade pip
   echo "Virtualenv created."
fi

# activate the virtual env
if [ ! $VIRTUAL_ENV ]; then
   source $BASEDIR/$VENVDIR/bin/activate
   echo "Virtualenv activated."
fi

# install pip requirements
if \
pip install cryptography --global-option=build_ext --global-option="-L/usr/local/opt/openssl/lib" --global-option="-I/usr/local/opt/openssl/include" && \
pip install -r $REQUIREMENTS && \
cd $BASEDIR/lib/xos-config; python setup.py install && \

#install xos-client
cp -R $BASEDIR/containers/xos/tmp.chameleon $BASEDIR/xos/xos_client/xosapi/chameleon && \
cd $BASEDIR/xos/xos_client/xosapi/chameleon/protos; VOLTHA_BASE=anything make && \
cd $BASEDIR/xos/xos_client; python setup.py install && \
chmod 777 $BASEDIR/venv-xos/lib/python2.7/site-packages/xosapi/chameleon/protoc_plugins/gw_gen.py && \
chmod 777 $BASEDIR/venv-xos/lib/python2.7/site-packages/xosapi/chameleon/protoc_plugins/swagger_gen.py && \
cd $BASEDIR/lib/xos-genx; python setup.py install
 then
   echo "Requirements installed."
   echo "Virtualenv ready"
 else
   echo "An error occurred"
fi
cd $BASEDIR
