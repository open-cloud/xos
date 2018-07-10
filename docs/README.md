# XOS Overview

XOS provides a framework for operationalizing a collection of
disaggregated components. More specifically, XOS defines an
*Extensible Service Control Plane*  that provides value in two
ways:

* It serves as a single unifying OAM interface to a collection of backend
  services, avoiding the operational silos that otherwise result from
  disaggregation. This includes a framework for creating and
  operating on services across organizational boundaries, across a range
  of implementation choices, and across multiple tenants.

* It manages end-to-end service chains across a service mesh, supporting
  visibility and control at the granularity of individual subscribers
  or flows. This provides a fine-grain means to correlate diagnostic and
  monitoring information, allocate resources and isolate performance,
  and distribute/migrate functionality.

XOS is currently being used in three projects:

* **CORD Controller:** XOS is a central part of CORD (Central Office
  Re-architected as a Datacenter), providing a coherent service
  control plane that runs on on top of a mix of disaggregated
  access technologies, legacy VNFs running in OpenStack VMs, horizontally
  scalable micro-services running in Kubernetes, and SDN control
  applications running on ONOS.

* **Network Edge Mediator (NEM):** XOS is being used to provide a
  mediation layer for SEBA (Software-Enabled Broadband Access),
  addressing the challenge of how to integrate an edge sites with different
  (and potentially multiple) global orchestrators and legacy OSS/BSS.

* **End-to-End Service Chains in a Multi-Cloud:** XOS is being used
  to manage end-to-end service chains that span customer premises,
  operator edge sites, Internet exchanges, and commodity clouds.

For additional white papers describing XOS, see the project
[wiki page](https://wiki.opencord.org/display/CORD/XOS+and+the+CORD+Controller).



