CONTAINER_NAME:=xos-server
IMAGE_NAME:=xosproject/xos
TOSCA_CONFIG_PATH:=/opt/xos/configurations/opencloud/opencloud.yaml
XOS_GIT_REPO?=git://github.com/open-cloud/xos.git
XOS_GIT_BRANCH?=master
NO_DOCKER_CACHE?=false

.PHONY: build
build: ; docker build --no-cache=${NO_DOCKER_CACHE} --rm -t ${IMAGE_NAME} . 

.PHONY: custom
custom: ; cat Dockerfile.templ | sed -e "s|XOS_GIT_REPO|${XOS_GIT_REPO}|g" -e "s|XOS_GIT_BRANCH|${XOS_GIT_BRANCH}|g" | docker build --no-cache=${NO_DOCKER_CACHE} -

.PHONY: run
run: ; docker run -d --name ${CONTAINER_NAME} -p 80:8000 ${IMAGE_NAME}

.PHONY: runtosca
runtosca: ; docker exec -it ${CONTAINER_NAME} /usr/bin/python /opt/xos/tosca/run.py padmin@vicci.org ${TOSCA_CONFIG_PATH}

.PHONY: stop
stop: ; docker stop ${CONTAINER_NAME}

.PHONY: rm
rm: ; docker rm ${CONTAINER_NAME}
