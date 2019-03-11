# Platform Services

XOS adopts an *Everything-as-a-Service* model. This includes
platform (infrastructure) services like Kubernetes and OpenStack.
Either or both can be integrated into an XOS-managed system,
and like any other service, they have models and synchronizers.
The only difference is that their models are part of the
[XOS core](core-models.md) (e.g., Slices, Instances, Networks) rather
than service extensions. This section describes three example platform
services in more detail:

* [Kubernetes](./external_content/kubernetes.md)
* [OpenStack](./external_content/openstack.md)
* [ONOS](./external_content/onos.md)

