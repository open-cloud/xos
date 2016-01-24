## Applications on XOS

This directory may prove to be unnecessary, but for now we
are using it for applications that run on top of the XOS API.
Initially, this includes only an auto-scaling app that uses
monitoring data to decide when to scale a service up/down.

This is treated as an application rather than yet another
service because it offers only a GUI front-end; it is not
modelled as a service that other services can build upon.
