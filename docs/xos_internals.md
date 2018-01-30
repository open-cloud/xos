# XOS Containers

XOS is made up of a set of Docker containers that cooperate to provide
platform controller functionaly, including the data model,
synchronizers, and northbound APIs. The following is an inventory of
those containers:

| Name | Description | Ports |
| ---- | ----------- | ----- |
| xos-core | The core of the platform, contains the model definition and the xProto toolchain | 50051, 500515 |
| xos-db | The Postgres instance that persists the data-model | 5432 |
| xos-redis | A Redis instance, used as pub/sub channel for internal notifications | 5432 |
| xos-tosca | Northbound TOSCA interface, accessible via REST at `/xos-tosca`| 9102|
| xos-gui | Northbound GUI interface, accessible at `/xos`| 4000|
| xos-ws | Listens to `redis` events and propagates them over web-sockets for notifications| 3000|
| xos-chameleon | Northbound REST interface, accessible at `/xosapi/v1/..` (`swagger` is published at `/apidocs/`| 3000|

Additionally some infrastructure helpers such as `consul` and `registrator` are  deployed to facilitate service discovery.

All the communication between containers happen over `gRPC` except for `xos-gui` 
where it is a combination of REST and web-socket.

![xos-containers](./static/xos_containers.png)
