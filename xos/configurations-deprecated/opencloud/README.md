# XOS OpenCloud Portal

This configuration can be used to bring up XOS on the OpenCloud portal.  It launches
XOS in three Docker containers (development GUI, Synchronizer, database) and configures XOS
with the `opencloud.yaml` TOSCA file in this directory.  *docker-compose* is used to manage
the containers.

## Docker Helpers

Stop the containers: `make stop`

Restart the containers: `make stop; make`

Delete the containers and relaunch them: `make rm; make`

Build the containers from scratch using the local XOS source tree: `make containers`

View logs: `make showlogs`

See what containers are running: `make ps`

Open a shell on the XOS container: `make enter-xos`

Open a shell on the Synchronizer container: `make enter-synchronizer`
