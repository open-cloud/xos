FROM ubuntu:14.04.2

RUN echo "deb http://packages.elasticsearch.org/logstash/1.5/debian stable main" | sudo tee -a /etc/apt/sources.list

RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y --force-yes \
    wget \
    ca-certificates \
    openjdk-7-jre-headless \
    supervisor \
    logstash



RUN mkdir /opt/logstash/plugins
ADD conf/supervisord.conf /etc/supervisor/conf.d/logstash.conf
ADD conf/logstash.conf /opt/logstash/logstash.conf
ADD conf/collectd-types.db /opt/logstash/collectd-types.db
ADD conf/filter_rsyslog.conf /etc/logstash/plugins/filter_rsyslog.conf

VOLUME ["/opt/logstash/certs"]

EXPOSE 514
EXPOSE 5043
EXPOSE 9292

CMD /usr/bin/supervisord -c /etc/supervisor/conf.d/logstash.conf
