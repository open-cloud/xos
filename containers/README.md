# XOS Docker Images

## Introduction

 XOS is comprised of 3 core services:

  * A database backend (postgres)
  * A webserver front end (django)
  * A synchronizer daemon that interacts with the openstack backend.

We have created separate dockerfiles for each of these services, making it
easier to build the services independently and also deploy and run them in
isolated environments.

#### Database Container

To build and run the database container:

```
$ cd postgres; make build && make run
```

#### XOS Container

To build and run the xos webserver container:

```
$ cd xos; make build && make run
```

You should now be able to access the login page by visiting
`http://localhost:8000` and log in using the default `padmin@vicci.org` account
with password `letmein`. It may be helpful to bootstrap xos with some sample
data; deployment, controllers, sites, slices, etc. You can get started by
loading tosca configuration for the opencloud demo dataset:

```
$ cd xos; make runtosca
```

Or you can create you own tosca configuraton file and customize the dataset
however you want. You can all load your own tosca configuration by setting the
`TOSCA_CONFIG_PATH` environment variable before executing the make command:

```
$ cd xos; TOSCA_CONFIG_PATH=/path/to/tosca/config.yaml make runtosca
```

#### Synchronizer Container

The Synchronizer shares many of the same dependencies as the xos container. The
synchronizer container takes advantage of this by building itself on top of the
xos image. This means you must build the xos image before building the
synchronizer image. The XOS and synchronizer containers can run on separate
hosts, but you must build the xos image on the host that you plan to run the
synchronizer container. Assuming you have already built the xos container,
executing the following will build and run the synchronizer container:

```
$ cd synchronizer; make build && make run
```

#### Solution Compose File ![](https://img.shields.io/badge/compose-beta-red.svg)

[Docker Compose](https://docs.docker.com/compose/) is a tool for defining and
running multi-container Docker applications. With Compose, you use a Compose
file to configure your application’s services. Then, using a single command, you
create, start, scale, and manage all the services from your configuration.

Included is a compose file in *YAML* format with content defined by the [Docker
Compose Format](https://docs.docker.com/compose/compose-file/). With the compose
file a complete XOS solution based on docker containers can be instantiated
using a single command. To start the instance you can use the command:

```
$ docker-compose -f xos-compose.yml up -d
```
