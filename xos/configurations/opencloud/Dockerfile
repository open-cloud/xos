FROM       ubuntu:14.04.2
MAINTAINER Andy Bavier <acb@cs.princeton.edu>

# Set environment variables.
ENV HOME /root
ENV TOSCA_CONFIG_PATH=/opt/xos/configurations/opencloud/opencloud.tosca

# XXX Workaround for docker bug:
# https://github.com/docker/docker/issues/6345
# Kernel 3.15 breaks docker, uss the line below as a workaround
# until there is a fix
RUN ln -s -f /bin/true /usr/bin/chfn
# XXX End workaround

# Install.
RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y \
    git \
    postgresql \
    graphviz \
    graphviz-dev \
    libxslt1.1 \
    libxslt1-dev \
    tar \
    gcc \
    geoip-database \
    libgeoip1 \
    openssh-client \
    wget \
    curl \
    python-dev \
    libyaml-dev \
    pkg-config \
    supervisor \
    python-crypto \
    python-httplib2>=0.9.1 \
    python-jinja2 \
    python-paramiko \
    python-pip \
    python-psycopg2 \
    python-pycurl \
    python-setuptools \
    python-yaml \
    python-keystoneclient \
    python-novaclient \
    python-neutronclient \
    python-glanceclient \
    python-ceilometerclient

RUN pip install \
    django==1.7 \
    djangorestframework==2.4.4 \
    markdown  \ 
    pyyaml \ 
    django-filter \
    lxml \
    netaddr \
    pytz \
    django-timezones \
    requests \
    django-crispy-forms \
    django-geoposition \
    django-extensions \
    django-suit \
    django-bitfield \
    django-ipware \
    django-encrypted-fields \
    django_rest_swagger \
    python-keyczar \
    pygraphviz \
    dnslib

RUN easy_install --upgrade httplib2

RUN easy_install \
    django_evolution \
    python_gflags \
    google_api_python_client \
    httplib2.ca_certs_locater


# Install custom Ansible
RUN git clone -b release1.8.2 git://github.com/ansible/ansible.git /opt/ansible
RUN git clone -b release1.8.2 git://github.com/ansible/ansible-modules-extras.git /opt/ansible/lib/ansible/modules/extras
RUN git clone -b release1.8.2 git://github.com/ansible/ansible-modules-extras.git /opt/ansible/v2/ansible/modules/extras
RUN git clone git://github.com/sb98052/ansible-modules-core.git /opt/ansible/lib/ansible/modules/core
RUN git clone git://github.com/sb98052/ansible-modules-core.git /opt/ansible/v2/ansible/modules/core
ADD ansible-hosts /etc/ansible/hosts

ADD http://code.jquery.com/jquery-1.9.1.min.js /usr/local/lib/python2.7/dist-packages/suit/static/suit/js/

# For Observer
RUN git clone git://git.planet-lab.org/fofum.git /tmp/fofum
RUN cd /tmp/fofum; python setup.py install
RUN rm -rf /tmp/fofum

RUN mkdir -p /usr/local/share /bin
ADD http://phantomjs.googlecode.com/files/phantomjs-1.7.0-linux-x86_64.tar.bz2 /usr/local/share/
RUN tar jxvf /usr/local/share/phantomjs-1.7.0-linux-x86_64.tar.bz2 -C /usr/local/share/
RUN rm -f /usr/local/share/phantomjs-1.7.0-linux-x86_64.tar.bz2
RUN ln -s /usr/local/share/phantomjs-1.7.0-linux-x86_64 /usr/local/share/phantomjs
RUN ln -s /usr/local/share/phantomjs/bin/phantomjs /bin/phantomjs

# Supervisor
ADD observer.conf /etc/supervisor/conf.d/

# Get XOS
RUN git clone git://github.com/open-cloud/xos.git /tmp/xos && mv /tmp/xos/xos /opt/

# Initscript is broken in Ubuntu
#ADD observer-initscript /etc/init.d/xosobserver

RUN chmod +x /opt/xos/scripts/opencloud
RUN /opt/xos/scripts/opencloud genkeys

# Workaround for AUFS issue
# https://github.com/docker/docker/issues/783#issuecomment-56013588
RUN mkdir /etc/ssl/private-copy; mv /etc/ssl/private/* /etc/ssl/private-copy/; rm -r /etc/ssl/private; mv /etc/ssl/private-copy /etc/ssl/private; chmod -R 0700 /etc/ssl/private; chown -R postgres /etc/ssl/private

# Set postgres password to match default value in settings.py
RUN service postgresql start; sudo -u postgres psql -c "alter user postgres with password 'password';"

# Turn DEBUG on so that devel server will serve static files
#    (not necessary if --insecure is passed to 'manage.py runserver')
# RUN sed -i 's/DEBUG = False/DEBUG = True/' /opt/xos/xos/settings.py

# Cruft to workaround problems with migrations, should go away...
RUN /opt/xos/scripts/opencloud remigrate

# git clone uses cached copy, doesn't pick up latest
RUN git -C /opt/ansible pull
RUN git -C /opt/ansible/lib/ansible/modules/core pull
RUN git -C /opt/ansible/v2/ansible/modules/core pull

# install Tosca engine
RUN apt-get install -y m4
RUN pip install python-dateutil
RUN bash /opt/xos/tosca/install_tosca.sh
RUN /usr/bin/python /opt/xos/tosca/run.py padmin@vicci.org ${TOSCA_CONFIG_PATH}

EXPOSE 8000

# Set environment variables.
ENV HOME /root

# Define working directory.
WORKDIR /root

# Define default command.
#CMD ["/bin/bash"]
CMD /opt/xos/scripts/docker_start_xos
