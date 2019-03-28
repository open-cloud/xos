# Copyright 2017 the original author or authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# Container are build via the `make build` commands.

# Optional parameters are:
# `REGISTRY=192.168.99.100:3000/ REPOSITORY=xosproject/ DOCKER_BUILD_ARGS="--no-cache" TAG=dev make build`

# Variables
VERSION                  ?= $(shell cat ../../VERSION)

## Docker related
DOCKER_REGISTRY          ?=
DOCKER_REPOSITORY        ?=
DOCKER_BUILD_ARGS        ?=
DOCKER_TAG               ?= ${VERSION}
DOCKER_IMAGENAME_BASE    := ${DOCKER_REGISTRY}${DOCKER_REPOSITORY}xos-base:${DOCKER_TAG}
DOCKER_IMAGENAME_LIBRARIES := ${DOCKER_REGISTRY}${DOCKER_REPOSITORY}xos-libraries:${DOCKER_TAG}
DOCKER_IMAGENAME_CLIENT  := ${DOCKER_REGISTRY}${DOCKER_REPOSITORY}xos-client:${DOCKER_TAG}
DOCKER_IMAGENAME_CORE    := ${DOCKER_REGISTRY}${DOCKER_REPOSITORY}xos-core:${DOCKER_TAG}
DOCKER_IMAGENAME_SYNC    := ${DOCKER_REGISTRY}${DOCKER_REPOSITORY}xos-synchronizer-base:${DOCKER_TAG}

summary:
	@echo Building images with:
	@echo "    Build args:    $(DOCKER_BUILD_ARGS)"
	@echo "    Registry:      ${DOCKER_REGISTRY}"
	@echo "    Repository:    ${DOCKER_REPOSITORY}"
	@echo "    Tag:           ${DOCKER_TAG}"

build: summary xos-base xos-libraries xos-client xos-core xos-synchronizer-base

xos-base:
	docker build $(DOCKER_BUILD_ARGS) -t ${DOCKER_IMAGENAME_BASE} -f Dockerfile.base .

xos-libraries:
	docker build --no-cache $(DOCKER_BUILD_ARGS) -t ${DOCKER_IMAGENAME_LIBRARIES} -f Dockerfile.libraries ../..

xos-client:
	docker build --no-cache $(DOCKER_BUILD_ARGS) -t ${DOCKER_IMAGENAME_CLIENT} -f Dockerfile.client ../..

xos-core:
	docker build --no-cache $(DOCKER_BUILD_ARGS) -t ${DOCKER_IMAGENAME_CORE} -f Dockerfile.xos-core ../..

xos-synchronizer-base:
	docker build --no-cache $(DOCKER_BUILD_ARGS) -t ${DOCKER_IMAGENAME_SYNC} -f Dockerfile.synchronizer-base ../..
