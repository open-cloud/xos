# How to setup a local dev environmnet

As now this is useful for working on libraries and will give you access to the `xossh` cli tool.

## Create a python virtual-env

We are providing an helper script to setup a python virtual environment and install all the required dependencies, to use it: 
```bash
source scripts/setup_venv.sh
```

At this point xos libraries are installed as python modules, so you can use any cli tool, for instance:
```bash
xossh
```
will open an xos shell to operate on models.
For more informations on `xossh` look at `xos/xos_client/README.md`

>NOTE: The `xossh` tool accept parameters to be configured, for example to use it against a local installation (frontend VM) you use:
>```bash
> xossh -G 192.168.46.100:50055 -S 192.168.46.100:50051
>```