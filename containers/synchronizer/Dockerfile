FROM       xosproject/xos

RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y \
    openssh-client \
    python-crypto \
    python-jinja2 \
    python-netaddr \
    python-paramiko \
    python-yaml \
    python-httplib2 \
    rsync \
    software-properties-common \
    supervisor

# required for ansible 2.0 OpenStack os_* modules
RUN pip install --upgrade pbr
RUN pip install --upgrade six
RUN pip install shade

# Install ansible from PPA
RUN add-apt-repository ppa:ansible/ansible
RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y \
    ansible

# For Synchronizer
RUN mkdir -p /usr/local/share /bin /etc/ansible

COPY conf/ansible-hosts /etc/ansible/hosts

# Supervisor
COPY conf/synchronizer.conf /etc/supervisor/conf.d/
CMD /usr/bin/supervisord -c /etc/supervisor/conf.d/synchronizer.conf
