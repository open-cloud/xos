FROM xosproject/xos-synchronizer-openstack

# Install docker-in-docker (dind). See https://hub.docker.com/_/docker/. The docker git repo
# currently only has 1.10 and 1.11, but it's possible to get the dockerfiles for earlier
# versions by using:
#        docker pull centurylink/dockerfile-from-image
#        alias dfimage="docker run -v /var/run/docker.sock:/var/run/docker.sock --rm centurylink/dockerfile-from-image"
#        dgimage <name of image>

# This container must be started in privileged mode.

# Install docker
ENV DOCKER_URL https://get.docker.com/builds/Linux/x86_64/docker-1.10.3
ENV DOCKER_SHA256 d0df512afa109006a450f41873634951e19ddabf8c7bd419caeb5a526032d86d

RUN curl -fLsS $DOCKER_URL -o docker && \
    echo "${DOCKER_SHA256}  docker" | sha256sum -c - && \
    mv docker /usr/local/bin/docker && \
    chmod +x /usr/local/bin/docker

# XXX uncomment the following 6 lines to run docker-in-docker
#     comment them out if using the docker socket in a volume instead
#ENV DIND_COMMIT=3b5fac462d21ca164b3778647420016315289034
#RUN wget "https://raw.githubusercontent.com/docker/docker/${DIND_COMMIT}/hack/dind" -O /usr/local/bin/dind && chmod +x /sr/local/bin/dind
#COPY start-dockerd.sh /usr/local/bin/
#VOLUME /var/lib/docker
#EXPOSE 2375
#ENTRYPOINT ["start-dockerd.sh"]

# Instead of using docker-in-docker, we can just attach ourselves
# to the docker socket via a volume in the docker-compose:
#     - /var/run/docker.sock:/var/run/docker.sock
# This is more convenient, allowing us to build directly into our
# parent's docker build system, making the images available for
# instantiation on the parent.

# Install docker-compose
ENV DOCKER_COMPOSE_URL https://github.com/docker/compose/releases/download/1.5.2/docker-compose-Linux-x86_64
ENV DOCKER_COMPOSE_SHA256 b6b975badc5389647ef1c16fe8a33bdc5935c61f6afd5a15a28ff765427d01e3

RUN curl -fLsS $DOCKER_COMPOSE_URL -o docker-compose && \
    echo "${DOCKER_COMPOSE_SHA256}  docker-compose" | sha256sum -c - && \
    mv docker-compose /usr/local/bin/docker-compose && \
    chmod +x /usr/local/bin/docker-compose

CMD /usr/bin/supervisord -c /etc/supervisor/conf.d/synchronizer.conf
