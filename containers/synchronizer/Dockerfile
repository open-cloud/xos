FROM       xosproject/xos

RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y \
    openssh-client \
    python-crypto \
    python-jinja2 \
    python-paramiko \
    python-yaml \
    python-httplib2 \
    rsync \
    supervisor

RUN pip install -U \
    jinja2

# Install custom Ansible
RUN \
    git clone -b release1.8.2 git://github.com/ansible/ansible.git /opt/ansible && \
    git clone -b release1.8.2 git://github.com/ansible/ansible-modules-extras.git /opt/ansible/lib/ansible/modules/extras && \
    git clone -b release1.8.2 git://github.com/ansible/ansible-modules-extras.git /opt/ansible/v2/ansible/modules/extras && \
    git clone git://github.com/sb98052/ansible-modules-core.git /opt/ansible/lib/ansible/modules/core && \
    git clone git://github.com/sb98052/ansible-modules-core.git /opt/ansible/v2/ansible/modules/core && \
    # git clone uses cached copy, doesn't pick up latest
    git -C /opt/ansible pull && \
    git -C /opt/ansible/lib/ansible/modules/core pull && \
    git -C /opt/ansible/v2/ansible/modules/core pull


# For Observer
RUN mkdir -p /usr/local/share /bin /etc/ansible

COPY conf/ansible-hosts /etc/ansible/hosts

ADD http://phantomjs.googlecode.com/files/phantomjs-1.7.0-linux-x86_64.tar.bz2 /usr/local/share/

RUN git clone git://git.planet-lab.org/fofum.git /tmp/fofum && \
    cd /tmp/fofum; python setup.py install && \
    rm -rf /tmp/fofum && \
    tar jxvf /usr/local/share/phantomjs-1.7.0-linux-x86_64.tar.bz2 -C /usr/local/share/ && \
    rm -f /usr/local/share/phantomjs-1.7.0-linux-x86_64.tar.bz2 && \
    ln -s /usr/local/share/phantomjs-1.7.0-linux-x86_64 /usr/local/share/phantomjs && \
    ln -s /usr/local/share/phantomjs/bin/phantomjs /bin/phantomjs


# Supervisor
COPY conf/synchronizer.conf /etc/supervisor/conf.d/

CMD update-ca-certificates && /usr/bin/supervisord -c /etc/supervisor/conf.d/synchronizer.conf
