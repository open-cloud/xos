# XOS ELK Stack Containers

## Introduction

ELK Stack is comprised of 3 core services:

  * A Elasticsearch database backend
  * A Logstash log collector 
  * A Kibana front end

We have created separate dockerfiles for each of these services, making it
easier to build and deploy the services independently.

#### Elasticsearch

To build the Elasticsearch container:

```
$ cd elasticsearch; make build && make run
```

#### Logstash

To build the Logstash container:

```
$ cd logstash; make build && make run
```

#### Kibana

To build the Kibana container:

```
$ cd kibana; make build && make run
```

### Forwarding logs to Logstash

Now that we have elk stack setup we need to start sending it some log files to process. We've provided a logstash-forwarder container that can be deployed on any host that has log files which you would like to have processed. 

#### Logstash-forwarder

The logstash-forwarder container is configured to mount the /var/log/ directory of the host machine, which means all files in /var/log are visible to the container. Modify the "files" section conf/config.json to include the files you want logstash-forwarder to handle. 

You can modify the mount options in the Makefile if you need to access files that live in a directory other than /var/log/.

To build the Loststash-forwarder container

```
$ cd logstash-forwarder; make build && make run
```

