FROM xosproject/xos-base

# Include certificates from Openstack
ADD local_certs.crt /usr/local/share/ca-certificates/local_certs.crt
RUN update-ca-certificates

# Install and boostrap XOS and Tosca
ENV XOS_GIT_REPO git://github.com/open-cloud/xos.git
ENV XOS_GIT_BRANCH master

RUN git clone $XOS_GIT_REPO -b $XOS_GIT_BRANCH /tmp/xos && \
    mv /tmp/xos/xos /opt/ && \
    chmod +x /opt/xos/tools/xos-manage && \
    /opt/xos/tools/xos-manage genkeys

# ng-xos-lib download

ENV NG_XOS_LIB_URL https://gerrit.opencord.org/ng-xos-lib

RUN git clone $NG_XOS_LIB_URL /tmp/ng-xos-lib 
RUN cp /tmp/ng-xos-lib/dist/ngXosHelpers.min.js /opt/xos/core/xoslib/static/js/vendor/ 
RUN cp /tmp/ng-xos-lib/dist/ngXosVendor.min.js /opt/xos/core/xoslib/static/js/vendor/

EXPOSE 8000

# Set environment variables
ENV HOME /root

# Define working directory
WORKDIR /opt/xos

# Define default command
CMD python /opt/xos/manage.py runserver 0.0.0.0:8000 --insecure --makemigrations

