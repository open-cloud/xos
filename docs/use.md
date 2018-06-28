# Using XOS

XOS has three inter-related aspects, and this section is
organized accordingly.

* **Modeling Framework:** XOS defines a
  [modeling framework](dev/xproto.md), which
  includes both a modeling language (*xproto*) and a generative
  toolchain (*xosgenx*). The abstractions that define a system's
  behavior are expressed in xproto, with xosgenx then used to
  generate code for several elements required to control the system
  (including an API that serves the set of models that have been
  loaded into XOS). Service developers typically write one or more
  models to on-board their service.

* **Synchronizer Framework:** XOS defines a
  [synchronization framework](dev/synchronizers.md)
  that actuates the XOS data model. This framework is reponsible for
  driving the underlying components configured into a system
  (for example, services, access devices) towards the desired state.
  Service developers typically write a synchronizer to on-board their
  services.

* **Core Models and Policies:** A system as a whole is defined by
  a [core](core_models.md) set of *xproto* models, plus a set of
  [security policies](security_policies.md) that govern how
  various principals can act on those models in a multi-tenant
  environment. Platform developers typically define and evolve the
  core models and policies, which effectively establishes the
  foundation on which all services run and are interconnected into
  service graphs.
