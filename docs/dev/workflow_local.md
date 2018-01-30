# Workflow: Local Scenario

The following describes a workflow for XOS core or GUI development using a
local environment (e.g., a laptop) with the local 'scenario'. To learn more
about the different POD config files, please refer to [Building and Installing
CORD](/install.md#included-scenarios).

The `local` scenario is suitable for working on (and verifying the correctness
of):

- `core` models
- `service` models
- `gui`

It runs in a set of local docker containers, and is the most lightweight of all
CORD development environments.

## Requirements

The following assumes you have cloned the source code as described in: [Getting
the Source Code](/getting_the_code.md).

To deploy a `local` scenario on your machine, you'll also need to install
[Docker](https://www.docker.com/community-edition).

These steps may be able to be automated by running the [cord-bootstrap.sh
script](/install.md#cord-bootstrapsh-script), with the `-d` option.

## Initial Deployment

You can setup a `local` POD config on your machine as follows.

```
cd ~/cord/build
make PODCONFIG=rcord-local.yml config
make build
```

After the build completes, the XOS web GUI will be available at
`localhost:8080/xos`

If you are using this on a remote node that uses Ubuntu as the base OS, you can
deploy an Apache proxy and set `/etc/hosts` variables to allow it to proxy the
connection remotely:

```
make local-ubuntu-dev-env
```

Example combining all of these using `cord-boostrap.sh`:

```
bash ./cord-bootstrap.sh -d -t "PODCONFIG=rcord-local.yml config" -t "local-ubuntu-dev-env" -t "build"
```

### Destroy and Rebuild XOS

This is the workflow that you'll need to follow if you want to start from a
fresh XOS installation. Note that it wipes the out the XOS database.

```
cd ~/cord/build
make local-xos-teardown
make build
```

To repeat all the build milestones, use `make clean-local`.

