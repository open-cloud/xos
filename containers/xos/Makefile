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

test:
	sudo docker build --no-cache=${NO_DOCKER_CACHE} --rm \
	-f Dockerfile.test -t xosproject/xos-test ${BUILD_ARGS} ../..

client:
	rm -rf tmp.chameleon
	cp -R /opt/cord/component/chameleon tmp.chameleon
	sudo docker build --no-cache=${NO_DOCKER_CACHE} --rm \
	--build-arg XOS_GIT_COMMIT_HASH="${XOS_GIT_COMMIT_HASH}" \
	--build-arg XOS_GIT_COMMIT_DATE="${XOS_GIT_COMMIT_DATE}" \
	-f Dockerfile.client -t xosproject/xos-client ${BUILD_ARGS} ../..
	rm -rf tmp.chameleon
	docker tag xosproject/xos-client:latest xosproject/xos-client:candidate

corebuilder:
	sudo docker build  --no-cache=${NO_DOCKER_CACHE} --rm \
        --build-arg XOS_GIT_COMMIT_HASH="${XOS_GIT_COMMIT_HASH}" \
        --build-arg XOS_GIT_COMMIT_DATE="${XOS_GIT_COMMIT_DATE}" \
        -f Dockerfile.corebuilder -t xosproject/xos-corebuilder ${BUILD_ARGS} ../..
	docker tag xosproject/xos-corebuilder:latest xosproject/xos-corebuilder:candidate

ui:
	sudo docker build  --no-cache=${NO_DOCKER_CACHE} --rm \
	--build-arg XOS_GIT_COMMIT_HASH="${XOS_GIT_COMMIT_HASH}" \
	--build-arg XOS_GIT_COMMIT_DATE="${XOS_GIT_COMMIT_DATE}" \
	-f Dockerfile.UI -t xosproject/xos-ui ${BUILD_ARGS} ../..
	docker tag xosproject/xos-ui:latest xosproject/xos-ui:candidate

synchronizer-base: 
	sudo docker build --no-cache=${NO_DOCKER_CACHE} --rm \
	-f Dockerfile.synchronizer-base -t xosproject/xos-synchronizer-base ${BUILD_ARGS} ../..
	docker tag xosproject/xos-synchronizer-base:latest xosproject/xos-synchronizer-base:candidate

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

