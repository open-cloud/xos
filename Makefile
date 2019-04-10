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
VERSION                  ?= $(shell cat ./VERSION)
CORE_NAME                ?= xos-core
CLIENT_NAME              ?= xos-client

## Testing related
XOS_LIBRARIES            := $(wildcard lib/*)

## Docker related
DOCKER_REGISTRY          ?=
DOCKER_REPOSITORY        ?=
DOCKER_BUILD_ARGS        ?=
DOCKER_TAG               ?= ${VERSION}
CORE_IMAGENAME           := ${DOCKER_REGISTRY}${DOCKER_REPOSITORY}${CORE_NAME}:${DOCKER_TAG}
CLIENT_IMAGENAME         := ${DOCKER_REGISTRY}${DOCKER_REPOSITORY}${CLIENT_NAME}:${DOCKER_TAG}

## Docker labels. Only set ref and commit date if committed
DOCKER_LABEL_VCS_URL     ?= $(shell git remote get-url $(shell git remote))
DOCKER_LABEL_VCS_REF     ?= $(shell git diff-index --quiet HEAD -- && git rev-parse HEAD || echo "unknown")
DOCKER_LABEL_COMMIT_DATE ?= $(shell git diff-index --quiet HEAD -- && git show -s --format=%cd --date=iso-strict HEAD || echo "unknown" )
DOCKER_LABEL_BUILD_DATE  ?= $(shell date -u "+%Y-%m-%dT%H:%M:%SZ")

# Targets
all: test

## Docker targets
docker-build:
	docker build $(DOCKER_BUILD_ARGS) \
    -t ${CORE_IMAGENAME} \
    --build-arg org_label_schema_version="${VERSION}" \
    --build-arg org_label_schema_vcs_url="${DOCKER_LABEL_VCS_URL}" \
    --build-arg org_label_schema_vcs_ref="${DOCKER_LABEL_VCS_REF}" \
    --build-arg org_label_schema_build_date="${DOCKER_LABEL_BUILD_DATE}" \
    --build-arg org_opencord_vcs_commit_date="${DOCKER_LABEL_COMMIT_DATE}" \
    -f Dockerfile.core .
	docker build $(DOCKER_BUILD_ARGS) \
    -t ${CLIENT_IMAGENAME} \
    --build-arg org_label_schema_version="${VERSION}" \
    --build-arg org_label_schema_vcs_url="${DOCKER_LABEL_VCS_URL}" \
    --build-arg org_label_schema_vcs_ref="${DOCKER_LABEL_VCS_REF}" \
    --build-arg org_label_schema_build_date="${DOCKER_LABEL_BUILD_DATE}" \
    --build-arg org_opencord_vcs_commit_date="${DOCKER_LABEL_COMMIT_DATE}" \
    -f Dockerfile.client .

docker-push:
	docker push ${CORE_IMAGENAME}
	docker push ${CLIENT_IMAGENAME}

# Create a virtualenv and install all the libraries
venv-xos:
	virtualenv $@;\
    source ./$@/bin/activate ; set -u ;\
    pip install -r requirements.txt nose2 mock requests_mock;\
    pip install -e lib/xos-util ;\
    pip install -e lib/xos-config ;\
    pip install -e lib/xos-genx ;\
    pip install -e lib/xos-kafka ;\
    pip install -e lib/xos-api ;\
    pip install -e lib/xos-synchronizer ;\
    pip install -e lib/xos-migrate

# tests
test: lib-test unit-test migration-test core-xproto-test

lib-test:
	for lib in $(XOS_LIBRARIES); do pushd $$lib; tox; popd; done

unit-test:
	tox

migration-test: venv-xos
	source ./venv-xos/bin/activate ; set -u ;\
    xos-migrate --xos-dir . -s core --check

create-migrations: venv-xos
	source ./venv-xos/bin/activate ; set -u ;\
        xos-migrate --xos-dir . -s core -v

core-xproto-test: venv-xos
	source ./venv-xos/bin/activate ; set -u ;\
    xosgenx xos/core/models/core.xproto --lint --strict

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

