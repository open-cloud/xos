# XOS UI Development

This configuration launches an XOS container on Cloudlab that runs the XOS develserver. The container is left running
in the backgorund.

The observer is not started, and there is no openstack backend connected for XOS. 

This configuration is intended for developing the XOS GUI. 

## Getting Started

- Navigate to '/xos/configurations/frontend' folder
- Run `make` command

You'll be able to visit XOS at `0.0.0.0:9000` and the `xos/core/xoslib` folder is shared with the container. This means that any update to that folder is automatically reported in the container.
