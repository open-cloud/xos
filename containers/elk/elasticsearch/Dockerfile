FROM ubuntu:14.04.2

RUN echo "deb http://packages.elastic.co/elasticsearch/1.7/debian stable main" | sudo tee -a /etc/apt/sources.list.d/elasticsearch-1.7.list

RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y --force-yes\
    openjdk-7-jre-headless \
    wget \
    elasticsearch

VOLUME ["/data"]

ADD conf/elasticsearch.yml /etc/elasticsearch/elasticsearch.yml
ADD conf/elasticsearch.yml /usr/share/elasticsearch/config

WORKDIR /data

# Expose ports.
#   - 9200: HTTP
#   - 9300: transport
EXPOSE 9200
EXPOSE 9300     

CMD ["/usr/share/elasticsearch/bin/elasticsearch"]
