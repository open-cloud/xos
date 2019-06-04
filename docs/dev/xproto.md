# XOS Modeling Framework

XOS defines a modeling framework: a language for specifying data models
(_xproto_) and a tool chain for generating code based on the set of models
(_xosgenx_).

The xproto language is based on [Google’s protocol
buffers](https://developers.google.com/protocol-buffers/) (protobufs),
borrowing their syntax, but extending their semantics to express additional
behavior. Although these extensions can be written in syntactically valid
protobufs (using the protobuf option feature), the resulting model definitions
are cumbersome and the semantics are under-specified.

Whereas protobufs primarily facilitate one operation on models, namely, data
serialization, xproto goes beyond protobufs to provide a framework for
implementing custom operators.

Users are free to define models using standard protobufs instead of the xproto
syntax, but doing so obscures the fact that packing new behavior into the
options field renders protobuf’s semantics under-specified. Full details are
given below, but as two examples: (1) xproto supports relationships (foreign
keys) among objects defined by the models, and (2) xproto supports boolean
predicates (policies) that can be applied to objects defined by the  models.

The xosgenx tool chain generates code based on a set of models loaded into the
XOS Core. This tool chain can be used to produce multiple targets, including:

* Object Relation Mapping (ORM) – maps the data model onto a persistent
  database.
* gRPC Interface – how all the other containers communicate with XOS Core.
* TOSCA API – one of the UI/Views used to access CORD.
* Security Policies – governs which principals can read/write which objects.
* Synchronizer Framework – execution environment in which Ansible playbooks
  run.
* Unit Tests – auto-generate API unit tests.

The rest of this section describes xproto: first the models and then policies that
can be applied to the models.

## Models

The xproto syntax for models is based on Google Protobufs. This means that any
protobuf file also qualifies as xproto. We currently use the Protobuf v2
syntax. For example, the file below specifies a model that describes container
images:

```protobuf
message Image {
     required string name = 1 [db_index = False, max_length = 256, null = False, content_type = "stripped", blank = False];
     required string kind = 2 [default = "vm", choices = "(('vm', 'Virtual Machine'), ('container', 'Container'))", max_length = 30, blank = False, null = False, db_index = False];
     required string disk_format = 3 [db_index = False, max_length = 256, null = False, content_type = "stripped", blank = False];
     required string container_format = 4 [db_index = False, max_length = 256, null = False, content_type = "stripped", blank = False];
     optional string path = 5 [max_length = 256, content_type = "stripped", blank = True, help_text = "Path to image on local disk", null = True, db_index = False];
     optional string tag = 6 [max_length = 256, content_type = "stripped", blank = True, help_text = "For Docker Images, tag of image", null = True, db_index = False];
}
```

We use standard protobuf scalar types, for example: `int32`, `uint32`,
`string`, `bool`, and `float`.

xproto contains several extensions, encoded as Protobuf options, which the
xosgenx toolchain recognizes at the top level. The xproto extensions to Google
Protobufs are as follows.

### Inheritance

Inheritance instructs the xproto processor that a model inherits the fields of
a set of base models. These base model fields are not copied into the derived
model automatically. However, the fields can be accessed in an xproto target.

* xproto

  ```protobuf
  message EC2Instance (Instance, EC2Object) {
        // EC2Instance inherits the fields of  Instance
  }
  ```

* protobuf

  ```protobuf
  message EC2Instance  {
        option bases = "Instance,EC2Object"
  }
  ```

### Links

Links are references to one model from another. A link specifies the type of
the reference (manytoone, manytomany, onetomany, or onetoone), name of the
field that contains the reference (_slice_ in the following example), its type
(e.g., _Slice_), the name of the field in the peer model that points back to
the current model, and a “through” field, specifying a model declared
separately as an xproto message, that stores properties of the link.

* xproto

  ```protobuf
  message Instance {
        required manytoone slice:Slice->instances = 1;
  }
  ```

* protobuf

  ```protobuf
  message Instance {
        required int32 slice = 1 [model="Slice", link="manytoone", src_port="slice", dst_port="instances"];
  }
  ```

The example shown below illustrates a manytomany link from Image to Deployment,
which goes through the model `ImageDeployments`:

* xproto

  ```protobuf
  required manytomany deployments->Deployment/ImageDeployments:images = 7 [help_text = "Select which images should be instantiated on this deployment", null = False, db_index = False, blank = True];
  ```

* protobuf

  ```protobuf
  required int32 deployments = 7 [help_text = "Select which images should be instantiated on this deployment", null = False, db_index = False, blank = True, model="Deployment", through="ImageDeployments", dst_port="images", link="manytomany"];
  ```

### Access Policies

Associates a policy (a boolean expression) with a model  to control access to
instances of that model. How policies (e.g., `slicle_policy`) are specified is
described below.

```protobuf
message Slice::slice_policy (XOSBase) {
…
}
```

### Model Options

Model Options declare information about models. They can be declared for
individual models, or at the top level in the xproto definition, in which case
they are inherited by all of the models in the file, unless they are overridden
by a particular model.

Currently supported model options include: `name`, `app_label`, `verbose_name`,
`custom_python`, `tosca_description`, `validators`, `plural`, `singular`, and
`gui_hidden`.

The name option is a short name used to refer to your service. For example, in
the Virtual Subscriber Gateway service, the name option is set to `vSG`.

```protobuf
option name = "vSG"
```

The app\_label option is a short programmatic name that does not need to be
easily understood by humans. It should not include whitespaces, and should
preferrably be all lowercase. If app\_label is not specified, then its value
defaults to the name option described above.

```protobuf
option app_label = "vsg"
```

The verbose\_name option contains a short description of the service.

```protobuf
option verbose_name = "Virtual Subscriber Gateway Service";
```

The `custom_python` option allows custom code to be attached to model.

```protobuf
option custom_python = "True"
```

The `custom_python` option is for services that require custom Python code in their
generated models. This option may either be specified at the file level and apply
to all models within a file, or individually at the model level within a file.
When custom python models are in use, the following changes occur to the generative
toolchain,

* Models are created in a file called "models_decl.py" (or modelname_decl.py depending
  on whether you're working on a service or in the core).
* Autogenerated models have the suffix `_decl` attached to them, for example
  `VSGService_decl`.
* If there's a mix of custom_python and non-custom_python models in the same file, then
  the non-custom_python models will automatically receive stubs that convert them
  from the `_decl` model to the non-`_decl` model.

Once the developer has designated some models as having custom python, it is then
up to the service developer to provide the final
models. The code below gives an example of custom models that inherit from such
intermediate `decl` models:

```python
class VSGService(VSGService__decl):
    def __xos_base_save(self, *args, **kwargs):
        self.prop1 = self.prop2 + self.prop3
    pass
```

You can use the xproto `service_extender` target to generate a stub for your
final model definitions.

> NOTE: As custom_python code ends up extending the XOS core with service-specific code,
> it is recommended to avoid using custom_python if an alternative exists to achieve
> the same functionality. For example, `model_policies` are another way to attach
> service-specific features to models, and run in the synchronizer rather than in the
> core.
>
> NOTE: The `custom_python` option was previously called `legacy`, and you may
> still encounter some services that use the keyword `legacy` instead of
> custom_python.

The plural and singular options provide the grammatically correct plural and
singular forms of your model name to ensure that autogenerated API endpoints
are valid.

```protobuf
option singular = "slice" # Singular of slice is not slouse, as computed by Python's pattern.en library

option plural = "ports" # Plural of ports is not portss
```

The tosca\_description option is a description for the service entry in the
autogenerated TOSCA schema.

The `validators` option contains a set of declarative object validators applied
to every object of the present model when it is saved. Validators are a comma
separated list of tuples, where the two elements of each tuple are separated by
a ':'. The first element of the tuple is a reference to an XOS policy
(described in another section of this document). The second element is an error
message that is returned to an API client that attempts an operation that does
not pass validation.

```protobuf
option validators = "instance_creator:Instance has no creator, instance_isolation: Container instance {obj.name} must use container image, instance_isolation_container_vm_parent:Container-vm instance {obj.name} must have a parent";
```

The gui\_hidden option is a directive to the XOS GUI to exclude the present
model from the default view provided to users.

```protobuf
option null = True
```

### Field Options

Options are also supported on a per-field basis. The following lists the
currently available field options.

The null option specifies whether a field has to be set or not (equivalent to
annotating the field as `required` or `optional`):

```protobuf
option null = True
```

Help text describes a field:

```protobuf
option help_text = “Descriptive text goes here”;
```

The default value of the field:

```protobuf
option default = “Default value of field”;
```

The maximum length of a field whose type is string:

```protobuf
option max_length = 128;
```

Whether a field can be empty:

```protobuf
option blank = False;
```

A label to be used by the GUI display for this field:

```protobuf
option verbose_name = “Verbose name goes here”;
```

A min/max value for the field

```protobuf
option min_value = 10;
option max_value = 100;
```

Designates a field as `feedback_state`, by default preventing it from being updated using GUI
or CLI tools.

```protobuf
option feedback_state = True;
```

Designates a field as `bookkeeping_state`, by default hiding it from GUI or CLI tools.

```protobuf
option bookkeeping_state = True;
```

Do not display this field in the GUI (also available at the model level):

```protobuf
option gui_hidden = True;
```

The set of valid values for a field, where each inner-tuple specifies
equivalence classes (e.g., vm is equivalent to Virtual Machine):

```protobuf
option choices = "(('vm', 'Virtual Machine'), ('container', 'Container'))";
```

Whether the field is an index field, that is, is used by database targets:

```protobuf
option db_index = True;
```

How to interpret/parse string fields:

```protobuf
option content_type = “stripped”;
option content_type = “date”;
option content_type = “url”;
option content_type = “ip”;
```

Whether an assignment to a field is permitted, where the option setting is a
named policy:

```protobuf
option validators = “port_validator:Slice is not allowed to connect to network”;
```

How policies (e.g., `port_validator`) are specified is described below.

Whether a field should be shown in the GUI:

```protobuf
option gui_hidden = True;
```

Identify a field that is used as key by the TOSCA engine. A model can have
multiple keys in case we need a composite key:

```protobuf
option tosca_key = True;
```

Identify a field that is used as key by the TOSCA engine. This needs to be used
in case a composite key can be composed by different combination of fields:

```protobuf
tosca_key_one_of = "<field_name>"
```

For example, in the `ServiceInstanceLink` model:

```protobuf
message ServiceInstanceLink (XOSBase) {
     required manytoone provider_service_instance->ServiceInstance:provided_links = 1 [db_index = True, null = False, blank = False, tosca_key=True];
     optional manytoone provider_service_interface->ServiceInterface:provided_links = 2 [db_index = True, null = True, blank = True];
     optional manytoone subscriber_service_instance->ServiceInstance:subscribed_links = 3 [db_index = True, null = True, blank = True];
     optional manytoone subscriber_service->Service:subscribed_links = 4 [db_index = True, null = True, blank = True, tosca_key_one_of=subscriber_service_instance];
     optional manytoone subscriber_network->Network:subscribed_links = 5 [db_index = True, null = True, blank = True, tosca_key_one_of=subscriber_service_instance];
}
```

the key is composed by `provider_service_instance` and one of
`subscriber_service_instance`, `subscriber_service`, `subscriber_network`

### Naming Conventions

Model names should use _CamelCase_ without underscore. Model names should
always be singular, never plural. For example: `Slice`, `Network`, `Site`.

Sometimes a model is used to relate two other models, and should be named after
the two models that it relates. For example, a model that relates the
`Controller` and `User` models should be called `ControllerUser`.

Field names use lower-case with underscores separating names. Examples of valid
field names are: name, `disk_format`, `controller_format`.

### Declarative vs Feedback vs Bookkeeping State

By convention, the fields that make up a model are classified as holding one of
three kinds of state: *declarative*, *feedback*, or *bookkeeping*.

Fields set by the operator to specify (declare) the expected state of CORD's
underlying components are said to hold *declarative state*.  In contrast,
fields that record operational data reported from CORD's underlying (backend)
components are said to hold *feedback state*.

*bookkeeping state* are fields that are typically used by the synchronizer
framework or by a synchronizer to hold information about the model that is
useful to the synchronizer, but not to the operator. For example, timestamps
that are used to track when models are dirty, error retry information,
etc.

For more information about declarative and feedback state, and the role they
play in synchornizing the data model with the backend components, read about
the [Synchronizer Architecture](sync_arch.md).

## Policies

Policies are boolean expressions that can be associated with models. Consider
two examples. In the first, `grant_policy` is a predicate applied to instances
of the `Privilege` model. It is used to generate and inject security checks
into the API.

```protobuf
policy grant_policy < ctx.user.is_admin
                      | exists Privilege:Privilege.object_type = obj.object_type
                        & Privilege.object_id = obj.object_id
                        & Privilege.accessor_type = "User"
                        & Privilege.accessor_id = ctx.user.id
                        & Privilege.permission = "role:admin" >

message Privilege::grant_policy (XOSBase) {
     required int32 accessor_id = 1 [null = False];
     required string accessor_type = 2 [null = False, max_length=1024];
     required int32 controller_id = 3 [null = True];
     required int32 object_id = 4 [null = False];
     required string object_type = 5 [null = False, max_length=1024];
     required string permission = 6 [null = False, default = "all", max_length=1024];
     required string granted = 7 [content_type = "date", auto_now_add = True, max_length=1024];
     required string expires = 8 [content_type = "date", null = True, max_length=1024];
}
```

The policy is executed relative to three implied inputs:

* The object on which the policy is invoked (e.g., `obj.object_type`).
* The context in which the policy is invoked (e.g., `cxt.user`).
* The data model as a whole (e.g., `exists Privilege:Privilege.accessor_id =
  ctx.user.id`).

Available context information includes the principal that invoked the operation
(`ctx.user`) and the type of access that principal is requesting
(`ctx.write_access` and `ctx.read_access`).

A second example involves the `Port` model and two related policies,
`port_validator` and `port_policy`.

```protobuf
policy port_validator < (obj.instance.slice in obj.network.permitted_slices.all()) | (obj.instance.slice = obj.network.owner) | obj.network.permit_all_slices >
policy port_policy < *instance_policy(instance) & *network_policy(network) >

message Port::port_policy (XOSBase) {
     option validators = "port_validator:Slice is not allowed to connect to network";
     required manytoone network->Network:links = 1 [db_index = True, null = False, blank = False, unique_with = "instance"];
     optional manytoone instance->Instance:ports = 2 [db_index = True, null = True, blank = True];
     optional string ip = 3 [max_length = 39, content_type = "ip", blank = True, help_text = "Instance ip address", null = True, db_index = False];
     optional string port_id = 4 [help_text = "Neutron port id", max_length = 256, null = True, db_index = False, blank = True];
     optional string mac = 5 [help_text = "MAC address associated with this port", max_length = 256, null = True, db_index = False, blank = True];
     required bool xos_created = 6 [default = False, null = False, db_index = False, blank = True];
}
```

Similar to the previous example, `port_policy` is associated with the `Port`
model, but unlike `grant_policy` shown above (which is an expression over a set
of objects in the data model), `port_policy` is defined by reference to two
other policies: `instance_policy` and `network_policy` (not shown).

This example also shows the use of _validators_, which enforce invariants on
how objects of a given model are used. In this case, policy `port_validator`
checks to make sure the slice associated with a given port is included in the
set of permitted networks.

Policy expressions may include the following operators:

* conjunction ( `&` ),
* disjunction ( `|` ),
* equality ( `=` ),
* negation ( `not` ),
* set membership ( `in` ),
* implication ( `->` ),
* qualifiers ( `exists`, `forall` ),
* sub-policy reference ( `* <policy name>` ),
* python escapes ({% raw %}`{{ python expression }}`{% endraw %}).


