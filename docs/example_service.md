# Example Service Tutorial

This tutorial uses
[ExampleService](https://github.com/opencord/exampleservice)
to illustrate how to write and on-board a service in CORD.
ExampleService is a multi-tenant service that instantiates a VM
instance on behalf of each tenant, and runs an Apache web server in
that VM. This web server is then configured to serve a
tenant-specified message (a string), where the tenant is able to set
this message using CORD's control interface. From a service
modeling perspective, *ExampleService* extends the base *Service*
model with two fields:

* `service_message`: A string that contains a message to display for
the service as a whole (i.e., to all tenants of the service).

* `tenant_message`: A string that is displayed for a specific Tenant.

## Summary

The result of preparing *ExampleService* for on-boarding is the
following set of files, all located in the `xos` directory of the
`exampleservice` repository. (There are other helper files, as described
throughout this tutorial.)

| Component | Source Code (https://github.com/opencord/exampleservice/) |
|----------|-----------------------------------------------------|
| Data Model  | `xos/exampleservice.xproto` |
| Synchronizer | `xos/synchronizer/steps/sync_exampletenant.py` `xos/synchronizer/steps/exampletenant_playbook.yaml` `xos/synchronizer/Dockerfile.synchronizer` |
| On-Boarding Spec	| `xos/exampleservice-onboard.yaml`

Earlier releases (3.0 and before) required additional
files (mostly Python code) to on-board a service, including a
REST API, a TOSCA API, and an Admin GUI. These components are now
auto-generated from the models rather than coded by hand, although it
is still possible to [extend the GUI](../xos-gui/developer/README.md).

## Development Environment

For this tutorial we recommend using
[CORD-in-a-Box (CiaB)](../quickstart.md) as your development
environment. By default CiaB brings up OpenStack, ONOS, and
XOS running the R-CORD collection of services.  This tutorial
demonstrates how to add a new customer-facing service to R-CORD.

CiaB includes a build machine, a head node, switches, and a compute
node all running as VMs on a single host.  Before proceeding you
should familiarize yourself with the CiaB environment.

Once you’ve prepared your CiaB, the development loop for
changing/building/testing service code involves these stages:

1. Make changes to your service code and propagate them to your CiaB
   host. There are a number of ways to propagate changes to the host
   depending on developer preference, including using gerrit draft
   reviews, git branches, rsync, scp, etc.
2. Build XOS container images on the build machine (corddev VM) and
   publish them to the head node (prod VM).  For this step, run the
   following commands in the corddev VM:
```
cd /cord/build
./gradlew -PdeployConfig=config/cord_in_a_box.yml PIprepPlatform
./gradlew :platform-install:buildImages
./gradlew -PdeployConfig=config/cord_in_a_box.yml :platform-install:publish
./gradlew -PdeployConfig=config/cord_in_a_box.yml :orchestration:xos:publish
```
3. Launch the new XOS containers on the head node (prod VM).  For this
   step, run the following commands in the prod VM (after the aliases
   have been defined for the first time, it's only necessary to run
   line 4):
```
alias xos-teardown="pushd /opt/cord/build/platform-install; ansible-playbook -i inventory/head-localhost --extra-vars  @/opt/cord/build/genconfig/config.yml teardown-playbook.yml; popd"
alias xos-launch="pushd /opt/cord/build/platform-install; ansible-playbook -i inventory/head-localhost --extra-vars @/opt/cord/build/genconfig/config.yml launch-xos-playbook.yml; popd"
alias compute-node-refresh="pushd /opt/cord/build/platform-install; ansible-playbook -i /etc/maas/ansible/pod-inventory --extra-vars=@/opt/cord/build/genconfig/config.yml compute-node-refresh-playbook.yml; popd"
xos-teardown; xos-launch; compute-node-refresh
```
4. Test and verify your changes
5. Go back to step #1

## Define a Model

The first step is to create a set of models for the service. To do
this, create a file named `exampleservice.xproto` in your service's `xos`
directory. This file encodes the models in the service in a format
called [xproto](../xos/dev/xproto.md) which is a combination of Google
Protocol Buffers and some XOS-specific annotations to facilitate the
generation of service components, such as the GRPC and REST APIs,
security policies, and database models among other things. It consists
of two parts:

* The Service model, which manages the service as a whole.

* The Tenant model, which manages tenant-specific
  (per-service-instance) state.

### Service Model

A Service model extends (inherits from) the XOS base *Service* model.
At its head is a set of option declarations: the name of the service as a
configuration string, and as a human readable one. Then follows a set
of field definitions.

```
message ExampleService (Service){
    option name = "exampleservice";
    option verbose_name = "Example Service";
    required string service_message = 1 [help_text = "Service Message to Display", max_length = 254, null = False, db_index = False, blank = False];
}
```

###Tenant Model

Your tenant model will extend the core `TenantWithContainer` class,
which is a Tenant that creates a VM instance:

```
message ExampleTenant (TenantWithContainer){
     option name = "exampletenant";
     option verbose_name = "Example Tenant";
     required string tenant_message = 1 [help_text = "Tenant Message to Display", max_length = 254, null = False, db_index = False, blank = False];
}
```

The following field specifies the message that will be displayed on a
per-Tenant basis:

```
tenant_message = models.CharField(max_length=254, help_text="Tenant Message to Display")
```

Think of this as a tenant-specific (per service instance) parameter.

## Define a Synchronizer

The second step is to define a synchronizer for the service.
Synchronizers are processes that run continuously, checking for
changes to service's model(s). When a synchronizer detects a change,
it applies that change to the underlying system. For *ExampleService*,
the Tenant model is the model we will want to synchronize, and the
underlying system is a compute instance. In this case, we’re using
`TenantWithContainer` to create this instance for us.

XOS Synchronizers are typically located in the `xos/synchronizer`
directory of your service.

>Note: Earlier versions included a tool to track model dependencies,
>but today it is sufficient to create a file named `model-deps` with
>the contents:` {}`.

The Synchronizer has two parts: A container that runs the
synchronizer process, and an Ansible playbook that configures the
underlying system. The following describes how to construct both.

###Synchronizer Container

First, create a file named `exampleservice-synchronizer.py`:

```
#!/usr/bin/env python
# Runs the standard XOS synchronizer
 
import importlib
import os
import sys
 
synchronizer_path = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), "../../synchronizers/new_base")
sys.path.append(synchronizer_path)
mod = importlib.import_module("xos-synchronizer")
mod.main()
```

The above is boilerplate. It loads and runs the default
`xos-synchronizer` module in it’s own Docker container.
To configure this module, create a file named
`exampleservice_from_api_config`, which specifies various
configuration and logging options:

```
# Sets options for the synchronizer
[observer]
name=exampleservice
dependency_graph=/opt/xos/synchronizers/exampleservice/model-deps
steps_dir=/opt/xos/synchronizers/exampleservice/steps
sys_dir=/opt/xos/synchronizers/exampleservice/sys
log_file=console
log_level=debug
pretend=False
backoff_disabled=True
save_ansible_output=True
proxy_ssh=True
proxy_ssh_key=/opt/cord_profile/node_key
proxy_ssh_user=root
enable_watchers=True
accessor_kind=api
accessor_password=@/opt/xos/services/exampleservice/credentials/xosadmin@opencord.org
required_models=ExampleService, ExampleTenant, ServiceDependency
```
>NOTE: Historically, synchronizers were named “observers”, so
>`s/observer/synchronizer/` when you come upon this term in the XOS
>code and documentation.

Second, create a directory within your synchronizer directory named `steps`. In
steps, create a file named `sync_exampletenant.py`:

```
import os
import sys
from synchronizers.new_base.SyncInstanceUsingAnsible import SyncInstanceUsingAnsible
from synchronizers.new_base.modelaccessor import *
from xos.logger import Logger, logging
 
parentdir = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, parentdir)
 
logger = Logger(level=logging.INFO)
 ```

Bring in some basic prerequities. Also include the models created
earlier, and `SyncInstanceUsingAnsible` which will run the Ansible
playbook in the Instance VM.

```
class SyncExampleTenant(SyncInstanceUsingAnsible):

provides = [ExampleTenant]
 
    observes = ExampleTenant
 
    requested_interval = 0
 
    template_name = "exampletenant_playbook.yaml"
 
    service_key_name = "/opt/xos/synchronizers/exampleservice/exampleservice_private_key"
 
    def __init__(self, *args, **kwargs):
        super(SyncExampleTenant, self).__init__(*args, **kwargs)
 
    def get_exampleservice(self, o):
        if not o.provider_service:
            return None
 
        exampleservice = ExampleService.objects.filter(id=o.provider_service.id)
 
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

```
export XOS_DIR=/opt/xos
python exampleservice-synchronizer.py  -C $XOS_DIR/synchronizers/exampleservice/exampleservice_from_api_config
```

Finally, create a Dockerfile for your synchronizer, name it
`Dockerfile.synchronizer` and place it in the `synchronizer` directory
with the other synchronizer files:

```
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
 
LABEL org.label-schema.schema-version=$org_label_schema_schema_version \
      org.label-schema.name=$org_label_schema_name \
      org.label-schema.version=$org_label_schema_version \
      org.label-schema.vcs-url=$org_label_schema_vcs_url \
      org.label-schema.vcs-ref=$org_label_schema_vcs_ref \
      org.label-schema.build-date=$org_label_schema_build_date \
      org.opencord.vcs-commit-date=$org_opencord_vcs_commit_date
 
CMD bash -c "cd /opt/xos/synchronizers/exampleservice; ./run-from-api.sh"
```

###Synchronizer Playbooks

In the same `steps` directory, create an Ansible playbook named
`exampletenant_playbook.yml` which is the “master playbook” for this set
of plays:

```
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
	
This sets some basic configuration, specifies the host this Instance
will run on, and the two variables that we’re passing to the playbook.

```
roles:
  - install_apache
  - create_index
```
  
This example uses Ansible’s Playbook Roles to organize steps, provide
default variables, organize files and templates, and allow for code
reuse. Roles are created by using a set directory structure.

In this case, there are two roles, one that installs Apache, and one
that creates the `index.html` file from a Jinja2 template.

Create a directory named `roles` inside `steps`, then create two
directories named for your roles: `install_apache` and `create_index`.

Within `install_apache`, create a directory named `tasks`, then within
that directory, a file named `main.yml`. This will contain the set of
plays for the `install_apache` role. To that file add the following:

```
- name: Install apache using apt
  apt:
    name=apache2
    update_cache=yes
```
	
This will use the Ansible apt module to install Apache.
	
Next, within `create_index`, create two directories, `tasks` and
`templates`. In `templates`, create a file named `index.html.j2`, with the
contents:

```
ExampleService
 Service Message: "{{ service_message }}"
 Tenant Message: "{{ tenant_message }}"
```
 
These Jinja2 Expressions will be replaced with the values of the
variables set in the master playbook.

In the `tasks` directory, create a file named `main.yml`, with the contents:

```
- name: Write index.html file to apache document root
  template:
    src=index.html.j2
    dest=/var/www/html/index.html
```

This uses the Ansible template module to load and process the Jinja2
template then put it in the `dest` location. Note that there is no path
given for the src parameter: Ansible knows to look in the templates
directory for templates used within a role.

As a final step, you can check your playbooks for best practices with
`ansible-lint` if you have it available.

## Define an On-boarding Spec

The final step is to define an on-boarding recipe for the service.
By convention, we use `<servicename>-onboard.yaml`, and place it in
the `xos` directory of the service.

The on-boarding recipe is a TOSCA specification that lists all of the
resources for your synchronizer. It's basically a collection of
everything that has been created above. For example, here is the
on-boarding recipe for *ExampleService*:

```
tosca_definitions_version: tosca_simple_yaml_1_0
 
description: Onboard the exampleservice
 
imports:
   - custom_types/xos.yaml
 
topology_template:
  node_templates:
    exampleservice:
      type: tosca.nodes.ServiceController
      properties:
          base_url: file:///opt/xos_services/exampleservice/xos/
          # The following will concatenate with base_url automatically, if
          # base_url is non-null.
          xproto: ./
          admin: admin.py
          tosca_custom_types: exampleservice.yaml
          tosca_resource: tosca/resources/exampleservice.py, tosca/resources/exampletenant.py
          rest_service: api/service/exampleservice.py
          rest_tenant: api/tenant/exampletenant.py
          private_key: file:///opt/xos/key_import/exampleservice_rsa
          public_key: file:///opt/xos/key_import/exampleservice_rsa.pub
```
		  
You will also need to modify the `profile-manifest` in `platform-install`
to on-board your service. To do this, modify the `xos_services` and
`xos_service_sshkeys` sections as shown below:

```
xos_services:
  ... (lines omitted)
  - name: exampleservice
    path: orchestration/xos_services/exampleservice
    keypair: exampleservice_rsa
    synchronizer: true
 
xos_service_sshkeys:
  ... (lines omitted)
  - name: exampleservice_rsa
    source_path: "~/.ssh/id_rsa"
```
	
The above modifications to the profile manifest will cause
the build procedure to automatically install an ssh key for your service,
and to onboard the service at build time.
