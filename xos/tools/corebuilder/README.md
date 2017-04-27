# Corebuilder #

Corebuilder is a build tool that is used to aid in generating the `xosproject/xos-ui` container image from the `xosproject/xos` container image. It does this by creating a `BUILD` tree that can be used to layer models and other files on top of the code base that is present in `xosproject/xos`. It's intended that corebuilder is run once to generate the BUILD tree, and then docker is run to generate the `xosproject/xos-ui` container image.  

TODO: Say something about how Corebuilder integrates xproto here.

## Running Corebuilder ##

Corebuilder is usually containerized and run from inside its container. See `Dockerfile.corebuilder` in `containers/xos` for reference on how the Corebuilder container is built. Running the corebuilder container usually requires a few docker volume mounts be used. For example, to run from the CORD dev node:

    docker run -it --rm -v /cord:/opt/cord -v /cord//orchestration/xos/containers/xos/BUILD:/opt/xos_corebuilder/BUILD /bin/bash docker-registry:5000/xosproject/xos-corebuilder:candidate <list of onboarding recipe pathnames>

In a typical CORD build, Corebuilder will be run automatically by the `xos-core-build` role of `platform-install`. 

## Running Unit Tests ##

The corebuilder container image includes the dependencies necessary to run the tool. If this container image is constructed, then the unit tests may be run as follows:

    docker run -it --rm --entrypoint python docker-registry:5000/xosproject/xos-corebuilder:candidate ./corebuilder_test.py

If the container image is not available, then the local environment can be setup to run the unit test directly.

1. Install the necessary python pip dependencies. See `containers/xos/pip_requirements.txt` for reference. At minimum, `tosca-parser==0.7.0` should be installed.
2. Create a directory, `custom_types` in the directory where `corebuilder_test.py` is to be run from.
3. Copy the contents of `xos/tosca/custom_types` to the `custom_types` directory created in step 2.
4. Execute `corebuilder_test.py`


