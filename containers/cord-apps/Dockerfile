FROM debian:jessie
MAINTAINER Andy Bavier <andy@onlab.us>

# Add Java 8 repository
ENV DEBIAN_FRONTEND noninteractive
RUN echo debconf shared/accepted-oracle-license-v1-1 select true | debconf-set-selections && \
    echo "deb http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main" | tee /etc/apt/sources.list.d/webupd8team-java.list && \
    echo "deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main" | tee -a /etc/apt/sources.list.d/webupd8team-java.list && \
    apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys EEA14886

# Set the environment variables
ENV HOME /root
ENV JAVA_HOME /usr/lib/jvm/java-8-oracle
ENV ONOS_ROOT /src/onos
ENV KARAF_VERSION 3.0.5
ENV KARAF_ROOT /root/onos/apache-karaf-3.0.5
ENV KARAF_LOG /root/onos/apache-karaf-3.0.5/data/log/karaf.log
ENV BUILD_NUMBER docker
ENV PATH $PATH:$KARAF_ROOT/bin

#Download build environment for ONOS
WORKDIR /src
RUN     apt-get update && apt-get install -y python maven git curl oracle-java8-installer oracle-java8-set-default && \
        git clone https://github.com/opennetworkinglab/onos.git && cd onos

RUN echo ". /src/onos/tools/dev/bash_profile" >> /root/.bashrc
