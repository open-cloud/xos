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

CONTAINER_NAME     ?= chameleon
IMAGE_NAME         ?= xosproject/chameleon

XOS_GIT_REPO       ?= https://github.com/opencord/xos.git
XOS_GIT_BRANCH     ?= master

XOS_GIT_COMMIT_HASH     ?= $(shell git log --pretty=format:'%H' -n 1 || echo -n "unknown" )
XOS_GIT_COMMIT_DATE     ?= $(shell git log --pretty=format:'%ad' -n 1 || echo -n "unknown" )

BUILD_ARGS =
ifdef http_proxy
BUILD_ARGS += --build-arg http_proxy=${http_proxy}
endif
ifdef https_proxy
BUILD_ARGS += --build-arg https_proxy=${https_proxy}
endif

chameleon:
	rm -rf tmp.chameleon
	cp -R /opt/cord/component/chameleon tmp.chameleon
	sudo docker build --no-cache=${NO_DOCKER_CACHE} --rm \
	-f Dockerfile.chameleon -t ${IMAGE_NAME} ${BUILD_ARGS} .
	rm -rf tmp.chameleon
