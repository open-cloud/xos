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

ifeq ($(TAG),)
TAG := candidate
endif

ifeq ($(REPOSITORY),)
REPOSITORY := xosproject/
endif

summary:
	@echo Building images with:
	@echo "    Build args:    $(DOCKER_BUILD_ARGS)"
	@echo "    Registry:      ${REGISTRY}"
	@echo "    Repository:    ${REPOSITORY}"
	@echo "    Tag:           ${TAG}"

build: summary xos-base xos-libraries xos-client xos-core xos-synchronizer-base

xos-base:
	docker build $(DOCKER_BUILD_ARGS) -t ${REGISTRY}${REPOSITORY}xos-base:${TAG} -f Dockerfile.base .

xos-libraries:
	docker build $(DOCKER_BUILD_ARGS) -t ${REGISTRY}${REPOSITORY}xos-libraries:${TAG} -f Dockerfile.libraries ../..

xos-client:
	rm -rf tmp.chameleon
	cp -R ../../../../component/chameleon tmp.chameleon
	docker build $(DOCKER_BUILD_ARGS) -t ${REGISTRY}${REPOSITORY}xos-client:${TAG} -f Dockerfile.client ../..

xos-core:
	docker build $(DOCKER_BUILD_ARGS) -t ${REGISTRY}${REPOSITORY}xos-core:${TAG} -f Dockerfile.xos-core ../..

xos-synchronizer-base:
	docker build $(DOCKER_BUILD_ARGS) -t ${REGISTRY}${REPOSITORY}xos-synchronizer-base:${TAG} -f Dockerfile.synchronizer-base ../..
