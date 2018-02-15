# Developing Synchronizers Using the Local Scenario

It is sometimes possible to develop a synchronizer entirely
within the local scenario. This results in a simple and efficient
development loop. A synchronizer can be developed locally
as long as:

* The VNF independently executes somewhere that you can connect to
from your local machine.
* The VNF does not require OpenStack be deployed as part of the POD.

> Note: The following assumes: (1) you have a local scenario up and
> running, with the service you are working on on-boarded; and (2) you
> obtained the source code as per [Getting the Code](/getting_the_code.md).

## Edit docker-compose File

A `docker-compose.yml` file was generated during the build process,
and it is located in the `cord_profile` directory that was also generated
(typically on the side of your root cord directory). For example, you
might find your compose file in `~/cord_profile/docker-compose.yml`.

Open it with you favorite editor and locate your service synchronizer.
You will need to add a `command: sleep 86440` to prevent the
synchronizer from starting automatically and a volume mount to share
the synchronizer code with your filesystem.

The following is an example of a modified synchronizer block; only the
meaningful fields have been reported:

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

The important bits are the sleep command and the last volume
mount. Leave everything else untouched.

## Development Loop

As a first step you will need to restart the local scenario to apply the
changes made in the `docker-compose` file.  To do this, use
`docker-compose` native commands. From the `cord_profile`
directory execute:

```shell
docker-compose -p <profile-name> up -d
```

> NOTE: The `<profile-name>` is the first part of any XOS container name, so
> you can easily discover it with `docker ps`.

At this point everything is up and running, except your synchronizer, which
is sleeping. Connect to the docker container with:

```shell
docker exec -it <synchronizer-container> bash
```

You will find yourself in the synchronizer folder. To start the synchronizer,
simply call `bash run.sh`.

> NOTE: The filename can be different, and you can also directly start the
> python process.

From now on, you can just make changes to the code on your local
filesystem and restart the process inside the container to see the changes.

## Additional Notes

If the VNF is running on your machine and you need to connect to
it, you can find the host IP address from inside a docker container using:

```shell
/sbin/ip route|awk '/default/ { print $3 }'
```

You can also easily have ONOS running on your local machine, and have
your synchronizer talk to it to verify expected behavior.

The same exact workflow will apply to changes made to model policies,
but if you make changes to the `xproto` model definition or to the `_decl`
model extension, you will have to rebuild the core container.

If the model changes are in the logic only (e.g., you are overriding the default
save method), you can rebuild and restart the container as follows:

```shell
rm milestones/local-start-xos && rm milestones/local-core-image && make build
```

If you made model changes (e.g., added or remove a field), you need to teardown
the database container and recreate it, so the command will be:

```shell
make xos-teardown && make build
```
