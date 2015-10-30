FROM       ubuntu:14.04.3

# XXX Workaround for docker bug:
# https://github.com/docker/docker/issues/6345
# Kernel 3.15 breaks docker, uss the line below as a workaround
# until there is a fix
RUN ln -s -f /bin/true /usr/bin/chfn
# XXX End workaround

# Install.
RUN apt-get update && apt-get install -y \
    git \
    postgresql \
    python-psycopg2 \
    graphviz \
    graphviz-dev \
    libxslt1.1 \
    libxslt1-dev \
    python-pip \
    tar \
    gcc \
    python-httplib2 \
    geoip-database \
    libgeoip1 \
    wget \
    curl \
    python-dev \
    libyaml-dev \
    pkg-config \
    python-pycurl

RUN pip install \
    django==1.7 \
    django-bitfield \
    django-crispy-forms \
    django-encrypted-fields \
    django-extensions
    django-filter \
    django-geoposition \
    django-ipware \
    django_rest_swagger \
    django-suit \
    django-timezones \
    djangorestframework==2.4.4 \
    dnslib
    lxml \  
    markdown \
    netaddr \
    python-dateutil \
    python-keyczar \
    pygraphviz
    pytz \
    pyyaml \
    requests


RUN DEBIAN_FRONTEND=noninteractive apt-get install -y python-setuptools
RUN easy_install django_evolution
RUN easy_install python_gflags
RUN easy_install --upgrade httplib2
RUN easy_install google_api_python_client
RUN easy_install httplib2.ca_certs_locater


# Get XOS
RUN git clone git://github.com/open-cloud/xos.git /tmp/xos && mv /tmp/xos/xos /opt/


# Initscript is broken in Ubuntu
#ADD observer-initscript /etc/init.d/xosobserver

RUN chmod +x /opt/xos/scripts/opencloud
RUN chmod +x /opt/xos/configurations/opencloud/run_opencloud
RUN /opt/xos/scripts/opencloud genkeys

# Turn DEBUG on so that devel server will serve static files
#    (not necessary if --insecure is passed to 'manage.py runserver')
# RUN sed -i 's/DEBUG = False/DEBUG = True/' /opt/xos/xos/settings.py

# Cruft to workaround problems with migrations, should go away...
RUN /opt/xos/scripts/opencloud remigrate

# install Tosca engine
RUN apt-get install -y m4
RUN bash /opt/xos/tosca/install_tosca.sh

EXPOSE 8000

# Set environment variables.
ENV HOME /root

# Define working directory.
WORKDIR /root

# Define default command.
CMD /opt/xos/configurations/opencloud/run_opencloud
