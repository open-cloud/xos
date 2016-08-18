# Docker container Makefile for XOS
#
# Targets:
#
#  `base`   - XOS prerequistie files, no XOS code, builds xosproject/xos-base
#  `build`  - base + XOS code, git pulled in Dockerfile from main repo,
#             builds xosproject/xos
#  `custom` - base + XOS code, git pulled in Dockerfile from selectable repo,
#             builds xosproject/xos
#  `devel`  - base + XOS code from local directory, builds xosproject/xos
#  `test`   - xosproject/xos + nodejs testing frameworks, builds
#             xosproject/xos-test
#

NO_DOCKER_CACHE    ?= false

CONTAINER_NAME     ?= xos-server
IMAGE_NAME         ?= xosproject/xos

XOS_GIT_REPO       ?= https://github.com/opencord/xos.git
XOS_GIT_BRANCH     ?= master

XOS_GIT_COMMIT_HASH     ?= $(shell git log --pretty=format:'%H' -n 1 || echo -n "unknown" )
XOS_GIT_COMMIT_DATE     ?= $(shell git log --pretty=format:'%ad' -n 1 || echo -n "unknown" )

TOSCA_CONFIG_PATH  ?= /opt/xos/configurations/opencloud/opencloud.yaml

BUILD_ARGS =
ifdef http_proxy
BUILD_ARGS += --build-arg http_proxy=${http_proxy}
endif
ifdef https_proxy
BUILD_ARGS += --build-arg https_proxy=${https_proxy}
endif

base:
	sudo docker build --no-cache=${NO_DOCKER_CACHE} --rm \
	-f Dockerfile.base -t xosproject/xos-base ${BUILD_ARGS} .

build:
	sudo docker build --no-cache=${NO_DOCKER_CACHE} --rm \
	-f Dockerfile -t ${IMAGE_NAME} ${BUILD_ARGS} .

custom:
	docker build --no-cache=${NO_DOCKER_CACHE} --rm \
	--build-arg XOS_GIT_REPO=${XOS_GIT_REPO} \
	--build-arg XOS_GIT_BRANCH=${XOS_GIT_BRANCH} \
	-f Dockerfile -t ${IMAGE_NAME} ${BUILD_ARGS} .

devel:
	sudo docker build --no-cache=${NO_DOCKER_CACHE} --rm \
	--build-arg XOS_GIT_COMMIT_HASH="${XOS_GIT_COMMIT_HASH}" \
	--build-arg XOS_GIT_COMMIT_DATE="${XOS_GIT_COMMIT_DATE}" \
	-f Dockerfile.devel -t ${IMAGE_NAME} ${BUILD_ARGS} ../..

test:
	sudo docker build --no-cache=${NO_DOCKER_CACHE} --rm \
	-f Dockerfile.test -t xosproject/xos-test ${BUILD_ARGS} ../..

run:
	sudo docker run -d --name ${CONTAINER_NAME} -p 80:8000 \
	${IMAGE_NAME}

runtosca:
	sudo docker exec -it ${CONTAINER_NAME} \
  /usr/bin/python /opt/xos/tosca/run.py padmin@vicci.org ${TOSCA_CONFIG_PATH}

stop:
	sudo docker stop ${CONTAINER_NAME}

rm:
	sudo docker rm ${CONTAINER_NAME}

rmi:
	sudo docker rmi `docker images | grep "^<none>" | awk '{print $$3}'`

