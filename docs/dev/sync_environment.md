# Synchronizer Development Environment

This page documents the Makefile and build environment for synchronizers.

## Setting up a synchronizer development environment

The synchronizer Makefile requires the following packages be installed:

* `Python`, preferably version 2.7 as well as a 3.x version
* `tox`, a framework for running unit tests. This should be installed using `pip`, as older versions obtainable via `apt` may be incompatible.
* `build-essentials` and `python-dev`, necessary to be able to setup the appropriate python virtual environments

When starting work on a new synchronizer, we recommend using the Makefile from and existing synchronizer (olt-service is a good working example) as a starting point rather than writing a Makefile from scratch.

## Targets available in the synchronizer Makefile

While each developer is free to create a custom Makefile, it is suggested for ease of integration that the following targets are available:

### make docker-build

Builds a docker container for the synchronizer. The environment variables `DOCKER_REGISTRY`. `DOCKER_REPOSITORY`, and `DOCKER_TAG` may be used to configure the name of the docker image that will be build. For example, the following command will build the image `myname/mysynchronizer:test`.

```bash
DOCKER_REPOSITORY=myname/mysynchronizer DOCKER_TAG=test make docker build
```

### make docker-push

This target will push a docker image that was built using `make docker-build` to dockerhub or another docker registry.

### make test

This target runs all tests on the repository that are appropriate for acceptance testing. Typically it invokes other Makefile targets such as `make test-unit`, `make test-migration`, and `make test-xproto`.

### make test-unit

This target runs `tox` to execute unit tests and generate a coverage report.

### make test-migration

This target checks that xproto migrations are up-to-date.

### make test-xproto

This target runs a linting check of the xproto files to ensure that the xproto is syntactically correct and that it obeys several semantic rules.

### make create-migration

This target will create or update the database migration scripts from the service's current xproto.

### make clean

This target removes all build artifacts, including the contents of virtual environments that are built, as well as unit testing coverage reports and results.