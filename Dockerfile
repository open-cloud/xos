FROM       ubuntu:14.04.1
MAINTAINER Andy Bavier <acb@cs.princeton.edu>

# XXX Workaround for docker bug:
# https://github.com/docker/docker/issues/6345
# Kernel 3.15 breaks docker, uss the line below as a workaround
# until there is a fix 
RUN ln -s -f /bin/true /usr/bin/chfn 
# XXX End workaround

# Install.
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y git
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y postgresql
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y python-psycopg2
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y graphviz graphviz-dev
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y libxslt1.1 libxslt1-dev
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y python-pip
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y tar
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y gcc
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y python-httplib2
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y geoip-database libgeoip1
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y wget
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y python-dev
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y libyaml-dev

RUN pip install django==1.7
RUN pip install djangorestframework==2.4.4
RUN pip install markdown  # Markdown support for the browseable API.
RUN pip install pyyaml    # YAML content-type support.
RUN pip install django-filter  # Filtering support
RUN pip install lxml  # XML manipulation library
RUN pip install netaddr # IP Addr library
RUN pip install pytz
RUN pip install django-timezones
RUN pip install requests
RUN pip install django-crispy-forms
RUN pip install django-geoposition
RUN pip install django-extensions
RUN pip install django-suit
RUN pip install django-evolution
RUN pip install django-bitfield
RUN pip install django-ipware
RUN pip install django-encrypted-fields
RUN pip install python-keyczar

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y python-keystoneclient
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y python-novaclient
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y python-neutronclient
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y python-glanceclient
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y python-ceilometerclient

RUN pip install django_rest_swagger

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y python-setuptools
RUN easy_install django_evolution
RUN easy_install python_gflags
RUN easy_install google_api_python_client

# Install custom Ansible
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y python-crypto
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y python-yaml
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y openssh-client
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y python-paramiko
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y python-jinja2
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y python-httplib2
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

RUN mkdir -p /usr/local/share /bin
ADD http://phantomjs.googlecode.com/files/phantomjs-1.7.0-linux-x86_64.tar.bz2 /usr/local/share/
RUN tar jxvf /usr/local/share/phantomjs-1.7.0-linux-x86_64.tar.bz2 -C /usr/local/share/
RUN rm -f /usr/local/share/phantomjs-1.7.0-linux-x86_64.tar.bz2
RUN ln -s /usr/local/share/phantomjs-1.7.0-linux-x86_64 /usr/local/share/phantomjs
RUN ln -s /usr/local/share/phantomjs/bin/phantomjs /bin/phantomjs

# Get XOS 
ADD xos /opt/xos

ADD observer-initscript /etc/init.d/plstackobserver

RUN chmod +x /opt/xos/scripts/opencloud
RUN /opt/xos/scripts/opencloud genkeys

# Set postgres password to match default value in settings.py
RUN service postgresql start; sudo -u postgres psql -c "alter user postgres with password 'password';"

# Turn DEBUG on so that devel server will serve static files
RUN sed -i 's/DEBUG = False/DEBUG = True/' /opt/xos/xos/settings.py

# Cruft to workaround problems with migrations, should go away...
RUN /opt/xos/scripts/opencloud remigrate

EXPOSE 8000

# Set environment variables.
ENV HOME /root

# Define working directory.
WORKDIR /root

# Define default command.
CMD ["/bin/bash"]
