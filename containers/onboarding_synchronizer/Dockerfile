FROM       xosproject/xos-synchronizer-openstack

# Install docker-in-docker (dind). See https://hub.docker.com/_/docker/. The docker git repo
# currently only has 1.10 and 1.11, but it's possible to get the dockerfiles for earlier
# versions by using:
#        docker pull centurylink/dockerfile-from-image
#        alias dfimage="docker run -v /var/run/docker.sock:/var/run/docker.sock --rm centurylink/dockerfile-from-image"
#        dgimage <name of image>

# This container must be started in privileged mode. 

RUN apt-get install -y curl

# XXX version 1.10.3
ENV DOCKER_BUCKET get.docker.com
ENV DOCKER_VERSION 1.10.3
ENV DOCKER_SHA256 d0df512afa109006a450f41873634951e19ddabf8c7bd419caeb5a526032d86d
RUN curl -fSL "https://${DOCKER_BUCKET}/builds/Linux/x86_64/docker-$DOCKER_VERSION" -o /usr/local/bin/docker && echo "${DOCKER_SHA256}  /usr/local/bin/docker" | sha256sum -c - && chmod +x /usr/local/bin/docker

# XXX vserioin 1.8.3
#ENV DOCKER_BUCKET=get.docker.com
#ENV DOCKER_VERSION=1.8.3
#ENV DOCKER_SHA256=f024bc65c45a3778cf07213d26016075e8172de8f6e4b5702bedde06c241650f
#RUN curl -fSL "https://${DOCKER_BUCKET}/builds/Linux/x86_64/docker-$DOCKER_VERSION" -o /usr/local/bin/docker && echo "${DOCKER_SHA256} /usr/local/bin/docker" | sha256sum -c - && chmod +x /usr/local/bin/docker

# XXX version 1.8.3
# XXX uncomment the following 6 lines to run docker-in-docker
#     comment them out if using the docker socket in a volume instead
#ENV DIND_COMMIT=3b5fac462d21ca164b3778647420016315289034
#RUN wget "https://raw.githubusercontent.com/docker/docker/${DIND_COMMIT}/hack/dind" -O /usr/local/bin/dind && chmod +x /usr/local/bin/dind
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

# Now install docker-compose

RUN bash -c "curl -L https://github.com/docker/compose/releases/download/1.5.2/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose"
RUN chmod +x /usr/local/bin/docker-compose

CMD update-ca-certificates && /usr/bin/supervisord -c /etc/supervisor/conf.d/synchronizer.conf
