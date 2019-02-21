# xos_api #

Xos\_api is a python library that is used by synchronizers and other components that need to communicate with the xos core. It includes a self-learning gRPC client (based on Chameleon) as well as a client-side ORM layer. 

Xos\_api includes a python setup.py program that may be used to install the library. As part of the standard CORD build, the container image xosproject/xos-client is created with xos_api already installed, so that it may easily be used as a base image for other components.  

## xossh ##

Xossh is a shell for interactively using the xos client API and client ORM layer. Generally xossh is run inside a container, and the xos\_client container is configured to run xossh as its default entrypoint. A script is provided in xos/tools to assist in invoking xossh from inside the head node environment. 

## Rebuilding Chameleon's protobuf API ##

The Chameleon API is expected not to change, and as such to facilitate build and deployment of xos-api, the Chameleon protobufs are distributed pre-built. If it is necessary to rebuild them, the following instructions may be helpful.

First, install the necessary prerequisite environment. This can be done by entering the xos virtualenv (see `scripts/setup_env.sh` from the root of this repository) or by installing the following pip packages: `protobuf==3.5.2`, `grpcio==1.12.0`, and `grpcio-tools==1.12.0`.

Then compile the protobuf files:

```bash
cd chameleon_client/protos
make
```

Finally, for each file you may wish to prepend an appropriate copyright header.