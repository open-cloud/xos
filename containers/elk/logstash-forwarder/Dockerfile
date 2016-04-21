FROM ubuntu:14.04.2

ENV LOGSTASH_HOST 66.228.36.77

RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y --force-yes \
    git \
    golang \
    supervisor

RUN git clone git://github.com/elasticsearch/logstash-forwarder.git /tmp/logstash-forwarder
RUN cd /tmp/logstash-forwarder && git checkout v0.4.0 && go build

RUN mkdir /opt/logstash-forwarder && cp /tmp/logstash-forwarder/logstash-forwarder /opt/logstash-forwarder/logstash-forwarder

ADD conf/config.json /opt/logstash-forwarder/config.json
ADD conf/supervisord.conf /etc/supervisor/conf.d/logstash-forwarder.conf
ADD run_logstash-forwarder /opt/logstash-forwarder/run_logstash-forwarder

RUN chmod +x /opt/logstash-forwarder/run_logstash-forwarder

RUN rm -rf /tmp/*

VOLUME ["/opt/certs", "/var/log/"]

CMD /opt/logstash-forwarder/run_logstash-forwarder


