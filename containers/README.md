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

To build the database container:

```
$ cd postgresql; make build
```

#### XOS Container

To build the XOS webserver container:

```
$ cd xos; make build
```

#### Synchronizer Container

The Synchronizer shares many of the same dependencies as the XOS container. The
synchronizer container takes advantage of this by building itself on top of the
XOS image. This means you must build the XOS image before building the
synchronizer image.  Assuming you have already built the XOS container,
executing the following will build the Synchronizer container:

```
$ cd synchronizer; make build
```

#### Solution Compose File

[Docker Compose](https://docs.docker.com/compose/) is a tool for defining and
running multi-container Docker applications. With Compose, you use a Compose
file to configure your application’s services. Then, using a single command, you
create, start, scale, and manage all the services from your configuration.

Included is a compose file in *YAML* format with content defined by the [Docker
Compose Format](https://docs.docker.com/compose/compose-file/). With the compose
file a complete XOS solution based on Docker containers can be instantiated
using a single command. To start the instance you can use the command:

```
$ docker-compose up -d
```

You should now be able to access the login page by visiting
`http://localhost:8000` and log in using the default `padmin@vicci.org` account
with password `letmein`.

## Configuring XOS for OpenStack

There are many possible configurations of XOS. The best way to get started
is to find the configuration that best matches your needs and modify it as
necessary. The available "canned" configurations can be found i `../xos/configurations/`.

If you have your own OpenStack cluster, and you would like to configure XOS to
control it, then take the following steps. Copy the `admin-openrc.sh` credentials 
file for your cluster to this directory.  Make sure that OpenStack commands work 
from the local machine using the credentials, e.g., `source ./admin-openrc.sh; nova list`.  Then run:

```
$ make
```

XOS will be launched (the Makefile will run the `docker-compose up -d` command
for you) and configured with the nodes and images available in your
OpenStack cloud.  You can then log in to XOS as described above and start creating
slices and instances.
