FROM       ubuntu:14.04.1
MAINTAINER Andy Bavier <acb@cs.princeton.edu>

# Install.
RUN apt-get update
RUN apt-get install -y git 
RUN apt-get install -y postgresql
RUN apt-get install -y python-psycopg2 
RUN apt-get install -y graphviz graphviz-dev
RUN apt-get install -y libxslt1.1 libxslt1-dev 
RUN apt-get install -y python-pip 
RUN apt-get install -y tar 
RUN apt-get install -y gcc 
RUN apt-get install -y python-httplib2 
RUN apt-get install -y geoip-database libgeoip1
RUN apt-get install -y wget
RUN apt-get install -y python-dev
RUN apt-get install -y libyaml-dev

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

RUN apt-get install -y python-keystoneclient
RUN apt-get install -y python-novaclient
RUN apt-get install -y python-neutronclient 
RUN apt-get install -y python-glanceclient
RUN apt-get install -y python-ceilometerclient

RUN pip install django_rest_swagger

RUN apt-get install -y python-setuptools
RUN easy_install django_evolution
RUN easy_install python_gflags
RUN easy_install google_api_python_client

# Set up latest Ansible
# Need to add our patches too
RUN apt-get install -y ansible
# RUN git clone --recursive git://github.com/ansible/ansible.git /opt/ansible
ADD ansible-hosts /etc/ansible/hosts

ADD http://code.jquery.com/jquery-1.9.1.min.js /usr/local/lib/python2.7/dist-packages/suit/static/suit/js/

# Get XOS 
ADD planetstack /opt/xos

ADD observer-initscript /etc/init.d/plstackobserver

RUN chmod +x /opt/xos/scripts/opencloud
RUN /opt/xos/scripts/opencloud genkeys

# Set postgres password to match default value in settings.py
RUN service postgresql start; sudo -u postgres psql -c "alter user postgres with password 'password';"

# Turn DEBUG on so that devel server will serve static files
RUN sed -i 's/DEBUG = False/DEBUG = True/' /opt/xos/planetstack/settings.py

# Cruft to workaround problems with migrations, should go away...
RUN /opt/xos/scripts/opencloud dropdb
RUN rm -rf /opt/xos/*/migrations
RUN cd /opt/xos; python ./manage.py makemigrations core
RUN cd /opt/xos; python ./manage.py makemigrations hpc
RUN cd /opt/xos; python ./manage.py makemigrations requestrouter
RUN cd /opt/xos; python ./manage.py makemigrations syndicate_storage
RUN cd /opt/xos; python ./manage.py makemigrations servcomp

RUN /opt/xos/scripts/opencloud initdb

EXPOSE 8000

# Set environment variables.
ENV HOME /root

# Define working directory.
WORKDIR /root

# Define default command.
CMD ["/bin/bash"]
