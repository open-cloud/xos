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

XOS currently has two use cases:

* **Network Edge Mediator (NEM):** XOS is being used to provide a
  mediation layer for CORD-based edge solutions, including SEBA
  (SDN-Enabled Broadband Access) and COMAC (Converged Multi-Access
  and Core). NEM replaces the "CORD Controller" component of earlier
  CORD solutions (e.g., R-CORD, M-CORD, and E-CORD).

* **End-to-End Service Chains in a Multi-Cloud:** XOS is being used
  to manage end-to-end service chains that span customer premises,
  operator edge sites, Internet exchanges, and commodity clouds.

For additional white papers describing XOS, see the project
[wiki page](https://wiki.opencord.org/display/CORD/XOS+and+NEM).



