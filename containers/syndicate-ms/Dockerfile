# Syndicate Metadata Server
# See also https://github.com/syndicate-storage/syndicate-docker

FROM ubuntu:14.04.4
MAINTAINER Zack Williams <zdw@cs.arizona.edu>

# vars
ENV APT_KEY butler_opencloud_cs_arizona_edu_pub.gpg
ENV MS_PORT 8080
ENV GAE_SDK google_appengine_1.9.35.zip

# Prep apt to be able to download over https
RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y --force-yes\
    apt-transport-https

# copy over and trust https cert
COPY butler.crt /usr/local/share/ca-certificates
RUN update-ca-certificates

# Install Syndicate MS
COPY $APT_KEY /tmp/
RUN apt-key add /tmp/$APT_KEY

RUN echo "deb https://butler.opencloud.cs.arizona.edu/repos/release/syndicate syndicate main" > /etc/apt/sources.list.d/butler.list

RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y --force-yes\
    syndicate-core \
    syndicate-ms \
    wget \
    unzip

# setup syndicate user
RUN groupadd -r syndicate && useradd -m -r -g syndicate syndicate
USER syndicate
ENV HOME /home/syndicate
WORKDIR $HOME

# setup GAE
RUN wget -nv https://storage.googleapis.com/appengine-sdks/featured/$GAE_SDK
RUN unzip -q $GAE_SDK

# Expose the MS port
EXPOSE $MS_PORT

# Create a storage location
RUN mkdir $HOME/datastore

# run the MS under GAE
CMD $HOME/google_appengine/dev_appserver.py --admin_host=0.0.0.0 --host=0.0.0.0 --storage_path=$HOME/datastore --skip_sdk_update_check=true /usr/src/syndicate/ms


