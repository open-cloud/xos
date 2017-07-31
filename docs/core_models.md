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
      virtualized resources (e.g., compute, network) in which the
      Service runs.

  In many CORD documents you will see mention of each service also
  having a "controller" but this effectively corresponds to the
  *Service* model itself, which is used to generate a "control
  interface" for the service. There is no explicit *Controller* model
  bound to a service. (There actually is a *Controller* model, but it
  represents the controller for a backend infrastructure service, such
  as OpenStack.)
   
* **ServiceInstance:** Represents an instance of a service
  instantiated on behalf of a particular tenant. This is a
  generalization of the idea of a Compute-as-a-Service spinning up
  individual "compute instances," or using another common
  example, the *ServiceInstance* corresponding to a Storage Service
  might be called a "Volume" or a "Bucket." Confusingly, there are
  also instances of a *Service* model that represent different
  services, but this is a consequence of standard modeling
  terminology, whereas  *ServiceInstance* is a core model in CORD
  (and yes, there are "instances of the *ServiceInstance* model").

* **ServiceDependency:** Represents a dependency between a *Subscriber*
Service on a *Provider*  Service. The set of ServiceDependency 
and Service models defined in CORD collectively represent the edges
and verticies of a *Service Graph*. (There is no explicit **ServiceGraph** model.)
The dependency between a pair of services is parameterized by the method
by which they are interconnected in the data plane. Connect methods include:

   - **None:** The two services are not connected in the data plane.
   - **Private:** The two services are connected by a common private network.
   - **Public:** The two services are connected by a publicly routable
   network.
   

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


* **User:** Represents an authenticated principal that is granted a set of
  privileges to invoke operations on a set of models, objects, and
  fields in the data model.

* **Privilege:** Represents the right to perform a set of read, write,
  or grant operations on a set of models, objects, and fields.

* **Site:** A logical grouping of Nodes that are co-located at the
  same geographic location, which also typically corresponds to the
  Nodes' location in the physical network.

  - Bound to a set of Users that are affiliated with the Site.

  - Bound to a set of Nodes located at the Site.

  The typical use case involves one configuration of a CORD POD 
  deployed at a single location. However, the underlying core includes 
  allows for multi-site deployments.
