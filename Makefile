# Copyright 2019-present Open Networking Foundation
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

# Makefile for testing and developing XOS

# set default shell
SHELL = bash -e -o pipefail

# Variables
XOS_LIBRARIES := $(wildcard lib/*)
XOS_DIR := "."

venv-xos:
	./scripts/setup_venv.sh

# tests
test: lib-test xos-test migration-test

lib-test:
	for lib in $(XOS_LIBRARIES); do pushd $$lib; tox; popd; done

xos-test: venv-xos
	source ./venv-xos/bin/activate ; set -u ;\
	nose2 -c tox.ini --verbose --junit-xml
	# FIXME: should run `flake8 xos` as a part of this target

migration-test: venv-xos
	source ./venv-xos/bin/activate ; set -u ;\
	xos-migrate --xos-dir . -s core --check

clean:
	find . -name '*.pyc' | xargs rm -f
	find . -name '__pycache__' | xargs rm -rf
	rm -rf \
    .coverage \
    coverage.xml \
    nose2-results.xml \
    venv-xos \
    lib/*/.tox \
    lib/*/build \
    lib/*/dist \
    lib/*/*.egg-info \
    lib/*/.coverage \
    lib/*/coverage.xml \
    lib/*/*results.xml \
    lib/*/*/VERSION \
    lib/xos-genx/xos-genx-tests/out/* \
    lib/xos-util/tests/test_version.py

