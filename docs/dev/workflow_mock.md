# Mock Workflow

The following describes a workflow for service or core development using a local 
environment (e.g., a laptop) with the `rcord-mock` or `rcord-single` profile. To learn more about scenarios you can refer to [Build Internals](../../build_internals.md#included-scenarios).

This workflow is suitable for working on (and verifying the
correctness of):

- `core` models
- `service` models
- `gui`
- `synchronizer` steps
- `profile` configurations

## Requirements

The following assumes you have cloned the source code as described 
in: [Getting the Source Code](../../cord_repo.md). 

To deploy a `mock` or a `single` scenario on your machine, you'll also
need to install [Vagrant](https://www.vagrantup.com/).

## Initial Deployment

You can setup a `mock` deployment on your machine as follows:

```
cd ~/cord/build
make PODCONFIG=rcord-mock.yml config
make -j4 build
```

This setups a `Vagrant VM`, and once the install is complete,
you can access:
- the XOS GUI at `192.168.46.100:8080/xos`
- the Vagrant VM via `ssh headnode`

### Configure Your Deployment

By default the `libvirt` provider is used to manage the Vagrant VM. 
If you prefer to use `VirtualBox` (this is the typical Mac OS case),
you can invoke the build command as:
```
VAGRANT_PROVIDER=virtualbox make -j4 build
```

The VM that is created as part of this lightweight deployment is configured
by default as:

| Scenario      | Memory        | Cores |
| ------------- |:-------------:| -----:|
| mock          | 2048          |     4 |
| single        | 4096          |     8 |

This configuration is defined in `~/cord/build/scenarios/mock/config.yaml` 
and `~/cord/build/scenarios/single/config.yaml`. You can
change those parameters to scale your development
VM up or down accordingly to the available resources.

## Development Loop

Note that the code is shared in the VM so that:
- `~/cord` is mounted on `/opt/cord`
- `~/cord_profile` is mounted on `/opt/cord_profile`
- `~/cord/platform-install/credentials/` is mounted on `~/opt/credentials` (only in the `single` scenario)

### Update the Code Running in the Containers

```
cd ~/cord/build
make xos-update-images
make -j4 build
```

### Destroy and Rebuild XOS

This is the workflow that you'll need to follow if you want 
to start from a fresh XOS installation. Note that it wipes the
out the XOS database.

```
cd ~/cord/build
make xos-teardown
make -j4 build
```

### Update the Profile Configuration
```
cd ~/cord/build
make clean-genconfig
make PODCONFIG=rcord-mock.yml config
make -j4 build
```
