IMAGE_NAME:=xosproject/cord-app-build
CONFIG_IMAGE_NAME:=xosproject/cord-app-config
VTN_IMAGE_NAME:=xosproject/cord-app-vtn
NO_DOCKER_CACHE?=false

BUILD_ARGS =
ifdef http_proxy
BUILD_ARGS += --build-arg http_proxy=${http_proxy}
endif
ifdef https_proxy
BUILD_ARGS += --build-arg https_proxy=${https_proxy}
endif

.PHONY: build
build: ; sudo docker build --no-cache=${NO_DOCKER_CACHE} --rm -t ${IMAGE_NAME} ${BUILD_ARGS} .

.PHONY: config
config: ; sudo docker build --rm -t ${CONFIG_IMAGE_NAME} -f Dockerfile.config ${BUILD_ARGS} .

.PHONY: vtn
vtn: ; sudo docker build --rm -t ${VTN_IMAGE_NAME} -f Dockerfile.vtn ${BUILD_ARGS} .
