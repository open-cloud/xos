# XOS Overview

XOS provides a framework for defining a set of declarative models and
then using those models to manage a collection of components that have
been configured into an operational system. XOS is itself deployed as
a set of micro-services, collectively forming an
*Extensible Service Control Plane* that:

* Serves as a single unifying interface to a collection of backend
  services, avoiding the management silos that otherwise result from
  disaggregation. This includes a framework for creating and
  operating on services across organizational boundaries, across a range
  of implementations, and across multiple tenants.

* Implements end-to-end service chains across a service mesh, supporting
  visibility and control at the granularity of individual subscribers
  or flows. This provides a fine-grain means to correlate diagnostic and
  monitoring information, allocate resources and isolate performance,
  and distribute/migrate functionality.

XOS is currently being used in three projects:

* **CORD Controller:** XOS is a central part of CORD, providing a coherent
  service control plane that runs on on top of a mix of disaggregated
  access technologies, legacy VNFs running in OpenStack VMs, horizontally
  scalable micro-services running in Kubernetes, and SDN control
  applications running on ONOS.

* **Network Edge Mediator (NEM):** XOS is being used to provide a
  mediation layer for SEBA (Software-Enabled Broadband Access),
  addressing the challenge of how to integrate an edge site with different
  (and potentially multiple) global orchestrators and legacy OSS/BSS.

* **End-to-End Service Chains in a Multi-Cloud:** XOS is being used
  to manage end-to-end service chains that span customer premises,
  edge sites, Internet exchange points, and commodity clouds.

For additional white papers describing XOS, see the project
[wiki page](https://wiki.opencord.org/display/CORD/XOS+and+the+CORD+Controller).



