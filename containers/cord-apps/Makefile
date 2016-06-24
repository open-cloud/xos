IMAGE_NAME:=xosproject/cord-app-build
CONFIG_IMAGE_NAME:=xosproject/cord-app-config
VTN_IMAGE_NAME:=xosproject/cord-app-vtn
NO_DOCKER_CACHE?=false

.PHONY: build
build: ; sudo docker build --no-cache=${NO_DOCKER_CACHE} --rm -t ${IMAGE_NAME} .

.PHONY: config
config: ; sudo docker build --rm -t ${CONFIG_IMAGE_NAME} -f Dockerfile.config .

.PHONY: vtn
vtn: ; sudo docker build --rm -t ${VTN_IMAGE_NAME} -f Dockerfile.vtn .
