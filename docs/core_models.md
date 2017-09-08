# Core Models

The XOS modeling framework provides a foundation for building CORD,
but it is just a means to defining the set of core models that effectively
specify CORD's architecture. 

## Overview

CORD's core starts with the **Service** model, which represents
all functionality that can be on-boarded into CORD. The power of the
Service model is that it is implementation-agnostic, supporting both
*server-based* services (e.g., legacy VNF running in VMs and
micro-services running in containers) and *switch-based* services
(e.g., SDN control applications that installs flow rules into
white-box switches).

To realize this range of implementation choices, each service is bound
a set of **Slice** models, each of which represents a
combination of virtualized compute resources (both containers and VMs)
and virtualized network resources (virtual networks).

Next, a **ServiceDependency** model represents a relationship betwee
a pair of services: a *subscriber*  and a *provider*. This dependency is
parameterized by a **connect_method** field that defines how the two
services are interconnected in the underlying network data plane. The
approach is general enough to interconnect two server-based services,
two switch-based services, or a server-based and a switch-based
service pair. This makes it possible to construct a service graph
without regard to how the underlying services are implemented.

For a service graph defined by a collection of Service and
ServiceDependency models, every time a subscriber requests service
(e.g., connects their cell phone or home router to CORD), a
**ServiceInstance** object is created to represent the virtualized
instance of each service traversed through the service graph on behalf
of that subscriber. Different subscribers may traverse different paths
through the service graph, based on their customer profile, but the
end result is a collection of interconnected ServiceInstance objects,
forming the CORD-equivalent of a service chain. (This "chain" is often
linear, but because the model allows for a many-to-many relationship
among service instances, it can form an arbitrary graph.)

Each node in this service chain (graph of ServiceInstance objects)
represents some combination of virtualized compute and network
resources; the service chain is not necessarily implemented by a
sequence of containers or VMs. That would be one possible
incarnation in the underlying service data plane, but how each
individual service instance is realized in the underlying resources
is an implementation detail. Moreover, because the data model
provides a way to represent this end-to-end service chain, it is
possible to access and control resources on a per-subscriber basis,
in addition to controlling them on a per-service basis.

Finally, each model defines a set of fields that are used to either
configure/control the underlying 
component (these fields are said to hold *declarative state*) or to 
record operational data about the underlying component (these 
fields are said to hold *feedback state*). For more information 
about declarative and feedback state, and the role they play in 
synchornizing the data model with the backend components,
read about the [Synchronizer Architecture](dev/sync_arch.md). 

## Model Glossary 

CORD's core models are defined by a set of [xproto](dev/xproto.md) 
specifications. They are defined in their full detail in the source 
code (see
[core.xproto](https://github.com/opencord/xos/blob/master/xos/core/models/core.xproto)).
The following summarizes these core models -- along with the 
key relationships (bindings) among them -- in words. 

* **Service:** Represents an elastically scalable, multi-tenant
program, including the declarative state needed to instantiate,
control, and scale functionality.

   - Bound to a set of `Slices` that contains the collection of
      virtualized resources (e.g., compute, network) in which the
      `Service` runs.

  In many CORD documents you will see mention of each service also
  having a "controller" which effectively corresponds to the
  `Service` model itself (i.e., its purpose is to generate a "control
  interface" for the service). There  is no "Controller" model
  bound to a service. (Confusingly, CORD does include a `Controller` 
  model, but it represents information about OpenStack. There is
  also a `ServiceController` construct in the TOSCA interface for
  CORD, which provides a means to load the `Service` model for
  a given service into CORD.)
   
* **ServiceDependency:** Represents a dependency between a *Subscriber*
service on a *Provider*  service. The set of `ServiceDependency` 
and `Service` models defined in CORD collectively represent the edges 
and verticies of a *Service Graph*, but there is no explicit
"ServiceGraph" model in CORD. The dependency between a pair of
services is parameterized by the `connect_method` by which the service are
interconnected in the data plane.Connect methods include:

   - **None:** The two services are not connected in the data plane. 
   - **Private:** The two services are connected by a common private network. 
   - **Public:** The two services are connected by a publicly routable 
   network. 
   

* **ServiceInstance:** Represents an instance of a service
  instantiated on behalf of a particular tenant. This is a
  generalization of the idea of a Compute-as-a-Service spinning up
  individual "compute instances," or using another common
  example, the `ServiceInstance` corresponding to a Storage Service
  might be called a "Volume" or a "Bucket." Confusingly, there are
  also instances of a `Service` model that represent different
  services, but this is a consequence of standard modeling
  terminology, whereas  `ServiceInstance` is a core model in CORD
  (and yes, there are instances of the `ServiceInstance` model).

* **ServiceInstanceLink:** Represents a logical connection between
`ServiceInstances` of two `Services`. A related model, `ServiceInterface`,
types the `ServiceInstanceLink` between two `ServiceInstances`. A
connected sequence of `ServiceInstances` and `ServiceInstanceLinks` form
what is often called a *Service Chain*, but there is no explicit
"ServiceChain" model in CORD.

* **Slice:** Represents a distributed resource container that includes
the compute and network resources that belong to (are used by) some
`Service`.

   - Bound to a set of `Instances` that provide compute resources for
      the `Slice`.

   - Bound to a set of `Networks` that connect the  slice's `Instances` to
      each other.
  
   - Bound to  a default `Flavor` that represents a bundle of
      resources (e.g., disk, memory, and cores) allocated to an
      instance. Current flavors borrow from EC2. 

   - Bound to a default `Image` that boots in each of the slice's`Instances`.
      Each `Image` implies a virtualization layer (e.g., Docker, KVM).


* **Instance:** Represents a single compute instance associated
   with a Slice and instantiated on some physical Node. Each Instance
   is of some `isolation` type: `vm` (implemented as a KVM virtual machine),
   `container` (implemented as a Docker container), or `container_vm`
   (implemented as a Docker container running inside a KVM virtual machine).

* **Network:** Represents a virtual network associated with a `Slice`. The
behavior of a given `Network`is defined by a `NetworkTemplate`, which
specifies a set of parameters, including `visibility` (set to `public` or
`private`),  `access` (set to `direct` or `indirect`), `translation`
(set to `none`or `nat`), and `topology_kind` (set to `bigswitch`,
`physical` or `custom`). There is also a `vtn_kind` parameter
(indicating the `Network` is manged by VTN), with possible settings:
`PRIVATE`, `PUBLIC`, `MANAGEMENT_LOCAL`, `MANAGEMENT_HOST`,
`VSG`, or `ACCESS__AGENT`.

* **Node:** Represents a physical server that can be virtualized and host Instances.

   - Bound to the `Site` where the `Node` is physically located.


* **User:** Represents an authenticated principal that is granted a set of
  privileges to invoke operations on a set of models, objects, and
  fields in the data model.

* **Privilege:** Represents the right to perform a set of read, write,
  or grant operations on a set of models, objects, and fields.

* **Site:** Represents a logical grouping of `Nodes` that are
  co-located at the same geographic location, which also typically
  corresponds to the nodes' location in the physical network.
  The typical use case involves one configuration of a CORD POD 
  deployed at a single location, although the underlying core includes 
  allows for multi-site deployments.

  - Bound to a set of `Nodes` located at the `Site`.



