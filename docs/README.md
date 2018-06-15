# Writing Models and Synchronizers

CORD adopts a model-based design, which is to say all aspects
of operating and managing CORD is mediated by a model-based
control plane. XOS is a tool that CORD uses to implement this
control plane. For an overview of XOS, see the following
white paper:
[XOS: Modeling-as-a-Service](https://wiki.opencord.org/display/CORD/XOS+and+the+CORD+Controller?preview=/1279317/4981376/XOS%20Modeling-as-a-Service.pdf).

XOS has three inter-related aspects, and this section is
organized accordingly.

* **Modeling Framework:** XOS defines a
  [modeling framework](dev/xproto.md), which
  includes both a modeling language (*xproto*) and a generative
  toolchain (*xosgenx*). The abstractions that define CORD's
  behavior are expressed in xproto, with xosgenx then used to
  generate code for several elements required to control CORD
  (including an API that serves the set of models that have been
  loaded into XOS). Service developers typically write one or more
  models to on-board their service.

* **Synchronizer Framework:** XOS defines a
  [synchronization framework](dev/synchronizers.md)
  that actuates the CORD data model. This framework is reponsible for
  driving the underlying components configured into CORD (for example,
  services, access devices) towards the desired state. Service developers
  typically write a synchronizer to on-board their services.
 
* **Core Models and Policies:** The CORD platform is defined by
  a [core](core_models.md) set of *xproto* models, plus a set of
  [security policies](security_policies.md) that govern how
  various principals can act on those models in a multi-tenant
  environment. Platform developers typically define and evolve the
  core models and policies, which effectively establishes the
  foundation on which all services run and are interconnected into
  service graphs.




