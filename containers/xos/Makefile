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

XOS_GIT_REPO       ?= git://github.com/open-cloud/xos.git
XOS_GIT_BRANCH     ?= master

TOSCA_CONFIG_PATH  ?= /opt/xos/configurations/opencloud/opencloud.yaml

base:
	sudo docker build --no-cache=${NO_DOCKER_CACHE} --rm \
	-f Dockerfile.base -t xosproject/xos-base .

build:
	sudo docker build --no-cache=${NO_DOCKER_CACHE} --rm \
	-f Dockerfile -t ${IMAGE_NAME} .

custom:
	docker build --no-cache=${NO_DOCKER_CACHE} --rm \
	--build-arg XOS_GIT_REPO=${XOS_GIT_REPO} \
	--build-arg XOS_GIT_BRANCH=${XOS_GIT_BRANCH} \
	-f Dockerfile -t ${IMAGE_NAME} .

devel:
	sudo docker build --no-cache=${NO_DOCKER_CACHE} --rm \
	-f Dockerfile.devel -t ${IMAGE_NAME} ../..

test:
	sudo docker build --no-cache=${NO_DOCKER_CACHE} --rm \
	-f Dockerfile.test -t xosproject/xos-test ../..

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

