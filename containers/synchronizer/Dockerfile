FROM       xosproject/xos

# Supervisor
COPY conf/synchronizer.conf /etc/supervisor/conf.d/

CMD /usr/bin/supervisord -c /etc/supervisor/conf.d/synchronizer.conf
