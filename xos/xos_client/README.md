# xos_client #

Xos\_client is a python library that is used by synchronizers and other components that need to communicate with the xos core. It includes a self-learning gRPC client (based on Chameleon) as well as a client-side ORM layer. 

Xos\_client includes a python setup.py program that may be used to install the library. As part of the standard CORD build, the container image xosproject/xos-client is created with xos_client already installed, so that it may easily be used as a base image for other components.  

## xossh ##

Xossh is a shell for interactively using the xos client API and client ORM layer. Generally xossh is run inside a container, and the xos\_client container is configured to run xossh as its default entrypoint. A script is provided in xos/tools to assist in invoking xossh from inside the head node environment. 

## Running Unit Tests ##

Some unit tests (orm\_test.py) optionally support an environment where the xos\_client library is installed, and a core API container is available to serve the API. This allows testing against the actual grpc client, instead of the mock-up. It's suggested that the xos-client container be used together with a frontend or CiaB installation.

    docker run --rm -it --entrypoint bash docker-registry:5000/xosproject/xos-client:candidate

Once inside of the container, run the test(s). For example,

    python /usr/local/lib/python2.7/dist-packages/xosapi/orm_test.py -R

The test may be run using a mock-up of the grpc client by omitting the -R option:
    
    python orm-test.py
