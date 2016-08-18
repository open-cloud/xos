FROM xosproject/xos-base

# Include certificates from Openstack
ADD local_certs.crt /usr/local/share/ca-certificates/local_certs.crt
RUN update-ca-certificates

# Install and boostrap XOS and Tosca
ENV XOS_GIT_REPO https://github.com/opencord/xos.git
ENV XOS_GIT_BRANCH master

RUN git clone $XOS_GIT_REPO -b $XOS_GIT_BRANCH /tmp/xos && \
    mv /tmp/xos/xos /opt/ && \
    chmod +x /opt/xos/tools/xos-manage && \
    /opt/xos/tools/xos-manage genkeys

# ng-xos-lib download

ENV NG_XOS_LIB_URL https://github.com/opencord/ng-xos-lib.git
ENV NG_XOS_LIB_VERSION 1.0.0

RUN git clone $NG_XOS_LIB_URL /tmp/ng-xos-lib 
RUN cd /tmp/ng-xos-lib && git checkout tags/$NG_XOS_LIB_VERSION
RUN cp /tmp/ng-xos-lib/dist/ngXosHelpers.min.js /opt/xos/core/xoslib/static/vendor/ 
RUN cp /tmp/ng-xos-lib/dist/ngXosVendor.min.js /opt/xos/core/xoslib/static/vendor/

EXPOSE 8000

# Set environment variables
ENV HOME /root

# Define working directory
WORKDIR /opt/xos

# Define default command
CMD python /opt/xos/manage.py runserver 0.0.0.0:8000 --insecure --makemigrations

