#!/bin/bash

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
cd $BASEDIR/lib/xos-config; python setup.py install
  then
    echo "Requirements installed."
    echo "Virtualenv ready"
  else
    echo "An error occurred"
fi
cd $BASEDIR
