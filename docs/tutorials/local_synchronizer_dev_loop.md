# Development of synchronizers in the local scenario

In some cases is possible to completely write a synchronizer in using the local
scenario, if that is possible for the integration with your VNF, this workflow
will speed up your development cycle by a lot.

Note that this document assume that you are already confident with writing XOS
services, the build system and the CORD terminology. It also assumes that you
have an XOS service in a good status.

It’s possible to work on a synchronizer locally as long as:

* The VNF can be executed somewhere that we can connect to from our machine
* The VNF does not require OpenStack to be deployed

> NOTE: Some of this steps can be used also in a more complex scenario, for
> example “virtual” also know as Cord-in-a-box

From now on this guide will assume that:

* you have a local scenario up and running, with the service you are working on
  onboarded

* You obtained the source code as per [Getting the Code](/getting_the_code.md)

## Tweak your docker-compose file

There are few changes you need to make to the docker-compose.yml file in order
to really shorten your development loop.

A `docker-compose.yml` file for XOS has been generated during the build and it
is located in the cord_profile directory.  Note that the cord_profile directory
is generated on the side of your cord root folder, so you should find your
compose file in `~/cord_profile/docker-compose.yml`

Open it with you favorite editor and locate your service synchronizer.  You’ll
need to add a `command: sleep 86440` to prevent the synchronizer from starting
automatically and a volume mount to share the synchronizer code with your
filesystem.

Here is an example of a modified synchronizer block (only the meaningful fields
have been reported here):

```yaml
<service>-synchronizer:
    image: xosproject/<servicename>-synchronizer:candidate
    command: sleep 86400
    volumes:
      - /home/user/cord_profile/xos_config_synchronizer.yaml:/opt/xos/xos_config.yaml:ro
      - /home/user/cord_profile/node_key:/opt/cord_profile/node_key:ro
      - /home/user/cord/build/platform-install/credentials:/opt/xos/services/<service>/credentials:ro
      - /home/user/cord_profile/im_cert_chain.pem:/usr/local/share/ca-certificates/local_certs.crt:ro
      - /home/user/cord/orchestration/xos_services/<service>/xos/synchronizer:/opt/xos/synchronizers/<service>
```

> NOTE: The important bits here are the sleep command and the last volume
> mount, leave everything else untouched.

## Development loop

As first we’ll need to restart the project to apply the changes we made in the
docker-compose file.  To do this we can use docker-compose native commands, so
from the `cord_profile` directory execute:

```shell
docker-compose -p <profile-name> up -d
```

> NOTE: The `<profile-name>` is the first part of any XOS container name, so
> you can easily discover it with `docker ps`.

At this point everything is up and running, except our synchronizer, since that
is up but sleeping.  We need to connect to the docker container with:

```shell
docker exec -it <synchronizer-container> bash
```

We’ll find ourself in the synchronizer folder, and to start the synchronizer
it’s enough to call `bash run.sh`.

> NOTE: The filename can be different here and you can also directly start the
> python process

From now on, you can just make changes at the code on your local filesystem and
restart the process inside the container to see the changes.

## Appendix

Note that if you have the VNF running on you machine and you need to connect to
it, you can find the host ip from inside a docker container using:

```shell
/sbin/ip route|awk '/default/ { print $3 }'
```

So you easily can have an onos running on you machine, and have your
synchronizer talk to it to quickly verify the changes.

The same exact workflow will apply to changes in model policies, while if you
make changes to the `xproto` model definition or to the `_decl` model
extension, you will have to rebuild the core container.

If the model changes are in the logic only (eg: you are overriding the default
save method) you can rebuild and restart the container, and here is a command
that you use:

```shell
rm milestones/local-start-xos && rm milestones/local-core-image && make build
```

While if you made model changes (eg: added/remove a field) you need to teardown
the database container and recreate it, so the command will be:

```shell
make xos-teardown && make build
```

