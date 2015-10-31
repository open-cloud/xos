FROM       xos

# Install custom Ansible
RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y \
    openssh-client \
    python-crypto \
    python-jinja2 \
    python-paramiko
    python-yaml \
    python-httplib2 \
    supervisor

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

RUN cp /tmp/xos/containers/observer/conf/ansible-hosts /etc/ansible/hosts

# For Observer
RUN mkdir -p /usr/local/share /bin

ADD http://phantomjs.googlecode.com/files/phantomjs-1.7.0-linux-x86_64.tar.bz2 /usr/local/share/

RUN git clone git://git.planet-lab.org/fofum.git /tmp/fofum && \
    cd /tmp/fofum; python setup.py install && \
    rm -rf /tmp/fofum && \
    tar jxvf /usr/local/share/phantomjs-1.7.0-linux-x86_64.tar.bz2 -C /usr/local/share/ && \
    rm -f /usr/local/share/phantomjs-1.7.0-linux-x86_64.tar.bz2 && \
    ln -s /usr/local/share/phantomjs-1.7.0-linux-x86_64 /usr/local/share/phantomjs && \
    ln -s /usr/local/share/phantomjs/bin/phantomjs /bin/phantomjs


# Supervisor
RUN cp /tmp/xos/containers/observer/conf/observer.conf /etc/supervisor/conf.d/

CMD /usr/bin/supervisord -c /etc/supervisor/conf.d/observer.conf
