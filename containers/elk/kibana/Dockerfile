FROM ubuntu:14.04.2

ENV KIBANA_VERSION kibana-4.0.1-linux-x64
ENV KIBANA_SECURE true
ENV KIBANA_USER kibana
ENV KIBANA_PASSWORD kibana

RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y \
    wget \ 
    nginx-full \
    apache2-utils \
    supervisor

WORKDIR /opt

RUN wget --no-check-certificate -O- https://download.elasticsearch.org/kibana/kibana/${KIBANA_VERSION}.tar.gz | tar xvfz -

RUN mkdir /etc/kibana # This is where the htpasswd file is placed by the run script

ADD conf/kibana /etc/nginx/sites-available/kibana

ADD conf/kibana-secure /etc/nginx/sites-available/kibana-secure

RUN rm /etc/nginx/sites-enabled/*

RUN echo "daemon off;" >> /etc/nginx/nginx.conf

ADD conf/supervisord.conf /etc/supervisor/conf.d/kibana.conf

ADD run_kibana /opt/${KIBANA_VERSION}/run_kibana

RUN chmod +x /opt/${KIBANA_VERSION}/run_kibana

EXPOSE 80
EXPOSE 5601

CMD /opt/${KIBANA_VERSION}/run_kibana
