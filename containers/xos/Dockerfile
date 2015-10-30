FROM ubuntu

RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y --force-yes \
    curl \
    gcc \
    geoip-database \
    git \
    graphviz \
    graphviz-dev \
    libgeoip1 \
    libxslt1.1 \
    libxslt1-dev \
    libyaml-dev \
    pkg-config \
    python-dev \
    python-httplib2 \
    python-pip \
    python-psycopg2 \
    python-pycurl \
    tar \
    wget

RUN pip install \
    lxml \
    netaddr \
    pytz \
    requests \
    python-keyczar \
    pygraphviz \
    dnslib

RUN easy_install \
    python_gflags \
    google_api_python_client \
    httplib2.ca_certs_locater

RUN easy_install --upgrade httplib2

