# Example Service Tutorial

This tutorial uses [ExampleService](https://github.com/opencord/exampleservice)
to illustrate how to write and on-board a service in CORD. *ExampleService* is a
multi-tenant service that instantiates a VM instance on behalf of each tenant,
and runs an Apache web server in that VM. This web server is then configured to
serve a tenant-specified message (a string), where the tenant is able to set
this message using CORD's control interface. From a service modeling
perspective, *ExampleService* extends the base *Service* model with two fields:

* `service_message`: A string that contains a message to display for the
  service as a whole (i.e., to all tenants of the service).
* `tenant_message`: A string that is displayed for a specific Tenant.

These two fields are a simple illustration of a common pattern. A service model
typically includes fields used to *configure* the service as a whole
(`service_message` in this example) and fields used to *control* individual
instances of the the service (`tenant_message` in this example). It would be
common for the operator to set configuration-related fields when the service
first starts up, and then set/adjust control-related fields on behalf of
individual tenants as the service runs.

Tenant and ServiceInstance are two closely related terms. "Tenant" refers to
the user or the consumer of a service. Often we partition a service into
logical partitions, each for use by a tenant, thus making it a multi-tenant
service. Each one of these tenant-specific partitions is referred to as a
ServiceInstance.

## Summary

The result of preparing *ExampleService* for on-boarding is the following set
of files, all located in the `xos` directory of the `exampleservice`
repository. When checked out, these files live in the
`CORD_ROOT/orchestration/xos-services/exampleservice` directory on
your local development machine.

| Component | Source Code (https://github.com/opencord/exampleservice/) |
|----------|-----------------------------------------------------|
| Data Model  | `xos/synchronizer/models/exampleservice.xproto` |
| Syncronizer Program | `xos/synchronizer/exampleservice-synchronizer.py` `xos/synchronizer/exampleservice_config.yaml` `xos/synchronizer/model-deps` `xos/synchronizer/Dockerfile.synchronizer` |
| Sync Steps  | `xos/synchronizer/steps/sync_exampletenant.py` `xos/synchronizer/steps/exampletenant_playbook.yaml` |
| Model Policies | `xos/synchronizer/model_policies/model_policy_exampleserviceinstance.py` |
| On-Boarding Spec | `xos/exampleservice-onboard.yaml`

In addition to implementing these service-specific files, the final step to
on-boarding a service requires you to modify an existing (or write a new)
[service profile](/service-profiles.md).  This tutorial uses the existing
R-CORD profile for illustrative purposes. These profile definitions currently
live in the
[https://github.com/opencord/rcord](https://github.com/opencord/rcord)
repository. Additional related playbooks reside in the
[https://github.com/opencord/platform-install/](https://github.com/opencord/platform-install/)
for historical reasons.

## Development Environment

For this tutorial we recommend using a [Virtual Pod (CiaB)](/install_virtual.md)
as your development environment. By default CiaB brings up OpenStack, ONOS, and
XOS running the R-CORD collection of services.  This tutorial demonstrates how
to add a new customer-facing service to R-CORD.

A Virtual Pod includes a build machine, a head node, switches, and a compute
node all running as VMs on a single host.  Before proceeding you should
familiarize yourself with the CiaB environment and the [POD Development
Loop](../dev/workflow_pod.md#development-loop).

## Create the synchronizer directory

The synchronizer directory holds the model declarations and the synchronizer
for the service. Usually this directory is `xos/synchronizer`. This tutorial
  will first walk through creating the models, and then discuss creating the
  synchronizer itself.

Make a new root directory for your service, and within that directory, create
an `xos` subdirectory. The `xos` subdirectory will hold all xos-related files
for your service.

Within the `xos` subdirectory, create a `synchronizer` subdirectory. The
`synchronizer` subdirectory holds the subset of files that end up built into
the `synchronizer` container image.

## Define a Model

Your models live in a file named `exampleservice.xproto` in your service's
`xos/synchronizer/models` directory. This file encodes the models in the
service in a format called [xproto](../dev/xproto.md) which is a combination of
Google Protocol Buffers and some XOS-specific annotations to facilitate the
generation of service components, such as the GRPC and REST APIs, security
policies, and database models among other things. It consists of two parts:

* The XPROTO Header, which contains options that are global to the rest of the file.

* The Service model, which manages the service as a whole.

* The ServiceInstance model, which manages tenant-specific
  (per-service-instance) state.

### XPROTO Header

Some options are typically specified at the top of your xproto file:

```protobuf
option name = "exampleservice";
option app_label = "exampleservice";
```

`name` specifies a name for your service. This is used as a default in several
places, for example it will be used for `app_label` if you don't specifically
choose an `app_label`. Normally it suffices to set this the name of your
service, lower case, with no spaces.

`app_label` configures the internal xos database application that is attached
to these models. As with `name`, it suffices to set this the name of your
service, lower case, with no spaces.

### Service Model (Service-wide state)

A Service model extends (inherits from) the XOS base *Service* model.  At its
head is a set of option declarations such as `verbose_name`, which specifies a
human-readable name for the service model. Then follows a set of field
definitions.

```protobuf
message ExampleService (Service){
    option verbose_name = "Example Service";
    required string service_message = 1 [help_text = "Service Message to Display", max_length = 254, null = False, db_index = False, blank = False];
}
```

### ServiceInstance Model (per-Tenant state)

Your ServiceInstance model will extend the core `TenantWithContainer` class,
which is a Tenant that creates a VM instance:

```protobuf
message ExampleServiceInstance (TenantWithContainer){
     option verbose_name = "Example Service Instance";
     required string tenant_message = 1 [help_text = "Tenant Message to Display", max_length = 254, null = False, db_index = False, blank = False];
}
```

The following field specifies the message that will be displayed on a
per-Tenant basis:

```protobuf
tenant_message = models.CharField(max_length=254, help_text="Tenant Message to Display")
```

Think of this as a tenant-specific (per service instance) parameter.

## Define a Synchronizer

The second step is to define a synchronizer for the service. Synchronizers are
processes that run continuously, checking for changes to service's model(s).
When a synchronizer detects a change, it applies that change to the underlying
system. For *ExampleService*, the `ServiceInstance` model is the model we will
want to synchronize, and the underlying system is a compute instance. In this
case, we’re using `TenantWithContainer` to create this instance for us.

XOS Synchronizers are typically located in the `xos/synchronizer` directory of
your service.

> Note: Earlier versions included a tool to track model dependencies, but today
> it is sufficient to create a file named `model-deps` with the contents: `{}`.

The Synchronizer has three parts: The synchronizer python program, model
policies which enact changes on the data model, and a playbook (typically
Ansible) that configures the underlying system. The following describes how to
construct these.

### Synchronizer Python Program

First, create a file named `exampleservice-synchronizer.py`:

```python
#!/usr/bin/env python
# Runs the standard XOS synchronizer

import importlib
import os
import sys
from xosconfig import Config

config_file = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + '/exampleservice_config.yaml')
Config.init(config_file, 'synchronizer-config-schema.yaml')

synchronizer_path = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), "../../synchronizers/new_base")
sys.path.append(synchronizer_path)
mod = importlib.import_module("xos-synchronizer")
mod.main()
```

The above is boilerplate. It loads and runs the default `xos-synchronizer`
module in it’s own Docker container.  To configure this module, create a file
named `exampleservice_config.yaml`, which specifies various configuration and
logging options:

```yaml
name: exampleservice
accessor:
  username: xosadmin@opencord.org
  password: "@/opt/xos/services/exampleservice/credentials/xosadmin@opencord.org"
required_models:
  - ExampleService
  - ExampleServiceInstance
  - ServiceDependency
  - ServiceMonitoringAgentInfo
dependency_graph: "/opt/xos/synchronizers/exampleservice/model-deps"
steps_dir: "/opt/xos/synchronizers/exampleservice/steps"
sys_dir: "/opt/xos/synchronizers/exampleservice/sys"
model_policies_dir: "/opt/xos/synchronizers/exampleservice/model_policies"
models_dir: "/opt/xos/synchronizers/exampleservice/models"
```

Make sure the `name` in your synchronizer config file is that same as the
app_label in your `xproto` file. Otherwise the models won't be dynamically
loaded correctly.

> NOTE: Historically, synchronizers were named “observers”, so
> `s/observer/synchronizer/` when you come upon this term in the XOS code and
> documentation.

Second, create a directory within your synchronizer directory named `steps`. In
steps, create a file named `sync_exampleserviceinstance.py`:

```python
import os
import sys
from synchronizers.new_base.SyncInstanceUsingAnsible import SyncInstanceUsingAnsible
from synchronizers.new_base.modelaccessor import *
from xos.logger import Logger, logging

parentdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, parentdir)

logger = Logger(level=logging.INFO)
```

Bring in some basic prerequisites. Also include the models created earlier, and
`SyncInstanceUsingAnsible` which will run the Ansible playbook in the Instance
VM.

```python
class SyncExampleServiceInstance(SyncInstanceUsingAnsible):

    provides = [ExampleServiceInstance]

    observes = ExampleServiceInstance

    requested_interval = 0

    template_name = "exampleserviceinstance_playbook.yaml"

    service_key_name = "/opt/xos/synchronizers/exampleservice/exampleservice_private_key"

    def __init__(self, *args, **kwargs):
        super(SyncExampleServiceInstance, self).__init__(*args, **kwargs)

    def get_exampleservice(self, o):
        if not o.owner:
            return None

        exampleservice = ExampleService.objects.filter(id=o.owner.id)

        if not exampleservice:
            return None

        return exampleservice[0]

    # Gets the attributes that are used by the Ansible template but are not
    # part of the set of default attributes.
    def get_extra_attributes(self, o):
        fields = {}
        fields['tenant_message'] = o.tenant_message
        exampleservice = self.get_exampleservice(o)
        fields['service_message'] = exampleservice.service_message
        return fields

    def delete_record(self, port):
        # Nothing needs to be done to delete an exampleservice; it goes away
        # when the instance holding the exampleservice is deleted.
        pass
```

Third, create a `run-from-api.sh` file for your synchronizer.

```shell
python exampleservice-synchronizer.py
```

Finally, create a Dockerfile for your synchronizer, name it
`Dockerfile.synchronizer` and place it in the `synchronizer` directory with the
other synchronizer files:

```dockerfile
FROM xosproject/xos-synchronizer-base:candidate

COPY . /opt/xos/synchronizers/exampleservice

ENTRYPOINT []

WORKDIR "/opt/xos/synchronizers/exampleservice"

# Label image
ARG org_label_schema_schema_version=1.0
ARG org_label_schema_name=exampleservice-synchronizer
ARG org_label_schema_version=unknown
ARG org_label_schema_vcs_url=unknown
ARG org_label_schema_vcs_ref=unknown
ARG org_label_schema_build_date=unknown
ARG org_opencord_vcs_commit_date=unknown
ARG org_opencord_component_chameleon_version=unknown
ARG org_opencord_component_chameleon_vcs_url=unknown
ARG org_opencord_component_chameleon_vcs_ref=unknown
ARG org_opencord_component_xos_version=unknown
ARG org_opencord_component_xos_vcs_url=unknown
ARG org_opencord_component_xos_vcs_ref=unknown

LABEL org.label-schema.schema-version=$org_label_schema_schema_version \
      org.label-schema.name=$org_label_schema_name \
      org.label-schema.version=$org_label_schema_version \
      org.label-schema.vcs-url=$org_label_schema_vcs_url \
      org.label-schema.vcs-ref=$org_label_schema_vcs_ref \
      org.label-schema.build-date=$org_label_schema_build_date \
      org.opencord.vcs-commit-date=$org_opencord_vcs_commit_date \
      org.opencord.component.chameleon.version=$org_opencord_component_chameleon_version \
      org.opencord.component.chameleon.vcs-url=$org_opencord_component_chameleon_vcs_url \
      org.opencord.component.chameleon.vcs-ref=$org_opencord_component_chameleon_vcs_ref \
      org.opencord.component.xos.version=$org_opencord_component_xos_version \
      org.opencord.component.xos.vcs-url=$org_opencord_component_xos_vcs_url \
      org.opencord.component.xos.vcs-ref=$org_opencord_component_xos_vcs_ref

CMD bash -c "cd /opt/xos/synchronizers/exampleservice; ./run-from-api.sh"
```

### Synchronizer Model Policies

Model policies are used to implement change within the data model. When an
`ExampleServiceInstance` object is saved, we want an `Instance` to be
automatically created that will hold the ExampleServiceInstance's web server.
Fortunately, there's a base class that implements this functionality for us, so
minimal coding needs to be done at this time. Create the `model_policies`
subdirectory and within that subdirectory create the file
`model_policy_exampleserviceinstance.py`:

```python
from synchronizers.new_base.modelaccessor import *
from synchronizers.new_base.model_policies.model_policy_tenantwithcontainer import TenantWithContainerPolicy

class ExampleServiceInstancePolicy(TenantWithContainerPolicy):
    model_name = "ExampleServiceInstance"
```

### Synchronizer Playbooks

In the same `steps` directory where you created
`sync_exampleserviceinstance.py`, create an Ansible playbook named
`exampleserviceinstance_playbook.yml` which is the “master playbook” for this
set of plays:

```yaml
# exampletenant_playbook

- hosts: "{{ instance_name }}"
  connection: ssh
  user: ubuntu
  sudo: yes
  gather_facts: no
  vars:
    - tenant_message: "{{ tenant_message }}"
    - service_message: "{{ service_message }}"
```

This sets some basic configuration, specifies the host this Instance will run
on, and the two variables that we’re passing to the playbook.

```yaml
roles:
  - install_apache
  - create_index
```

This example uses Ansible’s Playbook Roles to organize steps, provide default
variables, organize files and templates, and allow for code reuse. Roles are
created by using a set directory structure.

In this case, there are two roles, one that installs Apache, and one that
creates the `index.html` file from a Jinja2 template.

Create a directory named `roles` inside `steps`, then create two directories
named for your roles: `install_apache` and `create_index`.

Within `install_apache`, create a directory named `tasks`, then within that
directory, a file named `main.yml`. This will contain the set of plays for the
`install_apache` role. To that file add the following:

```yaml
- name: Install apache using apt
  apt:
    name=apache2
    update_cache=yes
```

This will use the Ansible apt module to install Apache.

Next, within `create_index`, create two directories, `tasks` and `templates`.
In `templates`, create a file named `index.html.j2`, with the contents:

```html
ExampleService
 Service Message: "{{ service_message }}"
 Tenant Message: "{{ tenant_message }}"
```

These Jinja2 Expressions will be replaced with the values of the variables set
in the master playbook.

In the `tasks` directory, create a file named `main.yml`, with the contents:

```yaml
- name: Write index.html file to apache document root
  template:
    src=index.html.j2
    dest=/var/www/html/index.html
```

This uses the Ansible template module to load and process the Jinja2 template
then put it in the `dest` location. Note that there is no path given for the
src parameter: Ansible knows to look in the templates directory for templates
used within a role.

As a final step, you can check your playbooks for best practices with
`ansible-lint` if you have it available.

## Define an On-boarding Spec

The next step is to define an on-boarding recipe for the service.  By
convention, we use `<servicename>-onboard.yaml`, and place it in the `xos`
directory of the service.

The on-boarding recipe is a TOSCA specification that lists all of the resources
for your synchronizer. For example, here is the on-boarding recipe for
  *ExampleService*:

```yaml
---
tosca_definitions_version: tosca_simple_yaml_1_0

description: Onboard the exampleservice

imports:
    - custom_types/xos.yaml

topology_template:
  node_templates:
    exampleservice:
      type: tosca.nodes.ServiceController
      properties:
          base_url: file:///opt/xos-services/exampleservice/xos/
          # The following will concatenate with base_url automatically, if
          # base_url is non-null.
          private_key: file:///opt/xos/key_import/exampleservice_rsa
          public_key: file:///opt/xos/key_import/exampleservice_rsa.pub
```

This is a legacy recipe that (when executed) on-boards *ExampleService* in the
sense that it registers the service with the system, but it does not provision
the service or create instances of the service. These latter steps can be done
through CORD's GUI or REST API, or by submitting yet other TOSCA workflows to a
running CORD POD (all based on end-points that are auto-generated from these
on-boarded models). Additional information on how to provision and use the
service is given in the last section of this tutorial.

NOTE: This file may soon be removed.

## Include the Service in a Profile

The final step to on-boarding a service is to include it in one or
more service profiles that are to be built and installed. Service
profiles are currently defined as part of the
[CORD build system](https://guide.opencord.org/install.html),
so this involves editing some build-related configuration files.
These files can be found in the `CORD_ROOT/orchestration/profiles/rcord` and `CORD_ROOT/build/platform-install`
directories of the checkout out source code.

### Profile Manifests

Inserting *ExampleService* in a service profile requires creating or
modifying one of the `.yml` files in
`orchestration/profiles/rcord` of your local repo.
In the following, we use `rcord.yml` as an illustrative example. There
are potentially three sections of this file that need attention.

First, modify the `xos-services` section to identify `exampleservice`
as a service to include in the profile. Doing this effectively points
the build system at the model and synchronizer specifications you've
just defined.

```yaml
xos-services:
  ... (lines omitted)...
  - name: exampleservice
    path: orchestration/xos-services/exampleservice
    keypair: exampleservice_rsa
    synchronizer: true
```

Second, optionally tell the build system to download and install
an image into CORD. In our particular case, *ExampleService*
uses the `trusty-server-multi-nic` that is included in R-CORD
for other purposes.

```yaml
xos_images:
  - name: "trusty-server-multi-nic".
    url: "http://www.vicci.org/opencloud/trusty-server-cloudimg-amd64-disk1.img.20170201"
    checksum:
    "sha256:ebf007ba3ec1043b7cd011fc6668e2a1d1d4c69c41071e8513ab355df7a057cb"
  ... (lines omitted)...
```

Third, optionally specify any GUI extensions associated with the
service. This is done in the `enabled_gui_extensions` section of
the profile manifest. ExampleService does not include a GUI extension.

### Other Build-Related Configuration

Today, a few other build-related configuration files require editing
to produce a deployment that includes ExampleService. (These details
will be hidden in future releases.)

* Add the service's synchronizer image to `build/docker_images.yml`

* Because the build system is integrated with the `git` and `repo` tools, if
  your service is not already checked into `gerrit.opencord.org`, you will also
  need to add the service to the manifest file `CORD_ROOT/.repo/manifest.xml`.
  Then run `git init` in the service’s source tree.

## Provision, Control, and Use the Service

Once *ExampleService*  is on-boarded into a running POD,
it is available to be provisioned, controlled and used. This can be
done via the CORD GUI or REST API, but the most common way is to
input a TOSCA workflow into the running POD. Typically, each service
contributes a TOSCA recipe to run as soon as the POD comes up
(i.e., as the last stage of the build system), so as to verify that the
installation was successful.

This recipe is generated from a `Jinja2`
template, which is customized at build-time with specific
details for the target POD (e.g., the site that hosts the POD). This
results in a `.yaml` TOSCA file that is passed to the deployed
POD and executed.

The *ExampleService*  template is defined by the following file:

```shell
build/platform-install/roles/exampleservice-config/templates/test-exampleservice.yaml.j2
```

It is an historical artifact that this template is in the
`build/platform-install/roles/exampleservice-config/templates`
directory. Templates for new services are instead located in
`build/platform-install/roles/cord-profile/templates`. For example,
see `template-service.yaml.j2` in that directory for a template
similar to the one used for *ExampleService*.

The first part of `test-exampleservice.yaml.j2` includes some
core object reference that *ExampleService* uses, for example,
the `trusty-server-multic-nic` image, the `small` flavor, and
both the `management_network` and the `public_network`.

```yaml
---
tosca_definitions_version: tosca_simple_yaml_1_0

imports:
   - custom_types/slice.yaml
   - custom_types/site.yaml
   - custom_types/image.yaml
   - custom_types/flavor.yaml
   - custom_types/network.yaml
   - custom_types/networktemplate.yaml
   - custom_types/networkslice.yaml
   - custom_types/exampleservice.yaml
   - custom_types/exampleserviceinstance.yaml

description: configure exampleservice

topology_template:
  node_templates:

# site, image, fully created in deployment.yaml
    {{ site_name }}:
      type: tosca.nodes.Site
      properties:
        must-exist: true
        name: {{ site_name }}

    m1.small:
      type: tosca.nodes.Flavor
      properties:
        name: m1.small
        must-exist: true

    trusty-server-multi-nic:
      type: tosca.nodes.Image
      properties:
        name: trusty-server-multi-nic
        must-exist: true

# private network template, fully created somewhere else
    private:
      type: tosca.nodes.NetworkTemplate
      properties:
        must-exist: true
        name: Private

# management networks, fully created in management-net.yaml
    management_network:
      type: tosca.nodes.Network
      properties:
        must-exist: true
        name: management

# public network, fully created somewhere else
    public_network:
      type: tosca.nodes.Network
      properties:
        must-exist: true
        name: public
```

This is followed by the specification of a `private` network used by
*ExampleService* :

```yaml
    exampleservice_network:
      type: tosca.nodes.Network
      properties:
          name: exampleservice_network
          labels: exampleservice_private_network
      requirements:
          - template:
              node: private
              relationship: tosca.relationships.BelongsToOne
          - owner:
              node: {{ site_name }}_exampleservice
              relationship: tosca.relationships.BelongsToOne
```

The next part of the workflow provisions the `Slice` (and related
instances and networks) in which *ExampleService*  runs. These
definitions reference the dependencies established above.

```yaml
# CORD Slices
    {{ site_name }}_exampleservice:
      description: Example Service Slice
      type: tosca.nodes.Slice
      properties:
          name: {{ site_name }}_exampleservice
          default_isolation: vm
          network: noauto
      requirements:
          - site:
              node: mysite
              relationship: tosca.relationships.BelongsToOne
          - service:
              node: exampleservice
              relationship: tosca.relationships.BelongsToOne
          - default_image:
              node: trusty-server-multi-nic
              relationship: tosca.relationships.BelongsToOne
          - default_flavor:
              node: m1.small
              relationship: tosca.relationships.BelongsToOne

# CORD NetworkSlices
    exampleservice_slice_management_network:
      type: tosca.nodes.NetworkSlice
      requirements:
        - network:
            node: management_network
            relationship: tosca.relationships.BelongsToOne
        - slice:
            node: {{ site_name }}_exampleservice
            relationship: tosca.relationships.BelongsToOne

    exampleservice_slice_public_network:
      type: tosca.nodes.NetworkSlice
      requirements:
        - network:
            node: public_network
            relationship: tosca.relationships.BelongsToOne
        - slice:
            node: {{ site_name }}_exampleservice
            relationship: tosca.relationships.BelongsToOne

    exampleservice_slice_exampleservice_network:
      type: tosca.nodes.NetworkSlice
      requirements:
        - network:
            node: exampleservice_network
            relationship: tosca.relationships.BelongsToOne
        - slice:
            node: {{ site_name }}_exampleservice
            relationship: tosca.relationships.BelongsToOne
```

Finally, the recipe instantiates the service object that represents
*ExampleService* (`exampleservice`) and spins up a Service Instance
on behalf of the first tenant (`exampletenant1`).

```yaml
   exampleservice:
      type: tosca.nodes.ExampleService
      properties:
        name: exampleservice
        public_key: {{ lookup('file', config_cord_profile_dir + '/key_import/exampleservice_rsa.pub') }}
        private_key_fn: /opt/xos/services/exampleservice/keys/exampleservice_rsa
        service_message: hello
      artifacts:
        pubkey: /opt/cord_profile/key_import/exampleservice_rsa.pub

    exampletenant1:
      type: tosca.nodes.ExampleServiceInstance
      properties:
        name: exampletenant1
        tenant_message: world
      requirements:
        - owner:
            node: exampleservice
            relationship: tosca.relationships.BelongsToOne
```

Note that these definitions initialize the `service_message` and
`tenant_message`, respectively. As a consequence, sending an HTTP GET request
to *ExampleService* will result in the response: `hello world`. Subsequently,
the user can interact with *ExampleService* via CORD's GUI or REST API to
change those values.

