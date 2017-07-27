#Core Models

CORD adopts a model-based design. Each service configured into a
given CORD deployment has a service-specific model, but CORD
also defines a set of core models. Service-specific models are
anchored in these core models.

CORD's core models are defined by a set of [xproto](dev/xproto.md)
specifications. They are defined in their full detail in the source
code. See:
[core.xproto](https://github.com/opencord/xos/blob/master/xos/core/models/core.xproto).
The following describes these core models -- along with the
relationships (bindings) among them -- in words.

* **Service:** Represents an elastically scalable, multi-tenant
program, including the means to instantiate, control, and scale
functionality.

   - Bound to a set of Slices that contains the collection of
      virtualized resources (e.g., compute, network) in which the Service runs.

   - Bound to a set of Controllers that represents the service's control 
      interface.

* **ServiceDependency:** Represents a dependency between a *Subscriber*
Service on a *Provider*  Service. The set of ServiceDependency 
and Service models defined in CORD collectively represent the edges
and verticies of a *Service Graph*. (There is no explicit **ServiceGraph** model.)
The dependency between a pair of services is parameterized by the method
by which they are interconnected in the data plane. Connect methods include:

   - **None:** The two services are not connected in the data plane.
   - **Private:** The two services are connected by a common private network.
   - **Public:** The two services are connected by a publicly routable network.

* **Slice:** A distributed resource container that includes the compute and 
network resources that belong to (are used by) some Service.

   - Bound to a (possibly empty) set of Instances that provide compute
      resources for the Slice. 

   - Bound to a set of Networks that connect the Slice's Instances to
      each other, and connect this Slice to the Slices of other Services.
  
   - Bound to a Flavor that defines how the Slice's Instances are 
      scheduled. 

   - Bound to an Image that boots in each of the Slice's Instances. 

* **Instance:** Represents a single compute instance associated
   with a Slice and instantiated on some physical Node. Each Instance
   is of some isolation type:

   - **VM:** The instance is implemented as a KVM virtual machine.
   - **Container:** The instance is implemented as a Docker container.
   - **Container-in-VM:** The instance is implemented as a Docker
      container running inside a KVM virtual machine.

* **Network:** A virtual network associated with a Slice. Networks are
of one of the following types:

   - **PRIVATE:** Virtual network for the instances in the same service
   - **PUBLIC:** Externally accessible network
   - **MANAGEMENT_LOCAL:** Instance management network which does not span
      compute nodes, only accessible from the host machine
   - **MANAGEMENT_HOST:** Real management network which spans compute and
 	  head nodes
   - **ACCESS_AGENT:** Network for access agent infrastructure service

* **Image:** A bootable image that runs in a virtual machine. Each 
  Image implies a virtualization layer (e.g., Docker, KVM), so the latter 
  need not be a distinct object. 

* **Flavor:** Represents a bundle of resources (e.g., disk, memory,
   and cores) allocated to an instance. Current flavors borrow from EC2. 

* **Controller:** Represents the binding of an object
  in the data model to a back-end element (e.g., an OpenStack head
  node).  Includes the credentials required to invoke the backend
  resource.

* **Node:** A physical server that can be virtualized and host Instances.

   - Bound to the Site where the Node is physically located.

   - Bound to a Deployment that defines the policies applied to the 
     Node. 

##Principals and Access Control

* **User:** Represents an authenticated principal that is granted a set of
  privileges to invoke operations on a set of models, objects, and
  fields in the data model.

* **Privilege:** Represents the right to perform a set of read, write,
  or grant operations on a set of models, objects, and fields.

##Sites and Deployments

The typical use case involves one configuration of a CORD POD
deployed at a single location. However, the underlying core includes
two models for multi-site/multi-configuration deployments:

* **Site:** A logical grouping of Nodes that are co-located at the
  same geographic location, which also typically corresponds to the
  Nodes' location in the physical network.

  - Bound to a set of Users that are affiliated with the Site.

  - Bound to a set of Nodes located at the Site.

  - Bound to a set of Deployments that the Site may access.

* **Deployment:** A logical grouping of Nodes running a compatible set
  of virtualization technologies and being managed according to a
  coherent set of resource allocation policies.

  - Bound to a set of Users that establish the Deployment's policies.

  - Bound to a set of Nodes that adhere to the Deployment's policies.

  - Bound to a set of supported Images that can be booted on the
    Deployment's nodes.

  - Bound to a set of Controllers that represent the back-end
    infrastructure service that provides cloud resources (e.g., an
    OpenStack head node).

Sites and Deployments are often one-to-one, which corresponds
to a each Site establishing its own policies, but in general,
Deployments may span multiple Sites. It is also possible that a single
Site hosts Nodes that belong to more than one Deployment. 

