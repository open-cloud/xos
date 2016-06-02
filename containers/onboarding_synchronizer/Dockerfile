FROM       xosproject/xos-synchronizer-openstack

RUN bash -c "which docker > /dev/null || wget -qO- https://get.docker.com/ | sh"
# | sh usermod -aG docker root"

CMD update-ca-certificates && /usr/bin/supervisord -c /etc/supervisor/conf.d/synchronizer.conf
