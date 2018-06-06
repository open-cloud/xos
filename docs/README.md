# Defining Models for CORD

CORD adopts a model-based design, which is to say all aspects
of operating and managing CORD is mediated by a model-based
control plane. XOS is the component in CORD that implements
this control plane. For an overview of XOS, see the following
white paper:
[XOS: Modeling-as-a-Service](https://wiki.opencord.org/display/CORD/XOS%3A+The+CORD+Controller?preview=/1279317/4981376/XOS%20Modeling-as-a-Service.pdf).

This guide describes XOS, and the role it plays in implementing CORD's
control plane. XOS is not a monolithic component. It is best viewed as
having three inter-related aspects, and this guide is organized accordingly.

First, XOS defines a [modeling framework](dev/xproto.md), which
includes both a modeling language (*xproto*) and a generative
toolchain (*xosgenx*). The core abstractions that define CORD's
behavior are expressed in xproto, with xosgenx then used to
generate code for several elements required to control CORD
(including an API that serves the set of models that have been
loaded into XOS).

Second, CORD is based on a core set of models. These models are
expressed and realized using XOS, but they are architecturally
independent of XOS. These models are central to defining what
CORD **is**, including its [core abstractions](core_models.md)
and the [security policies](security_policies.md) that govern how
various principals can act on those abstractions in a multi-tenant
environment.

Third, XOS defines a [synchronization framework](dev/synchronizers.md)
that actuates the CORD data model. This framework is reponsible for
driving the underlying components configured into CORD (for example,
services, access devices) towards the desired state.

