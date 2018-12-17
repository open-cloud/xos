# Tutorial

This section walks you through the process of writing an XOS
model and synchronizer. It does not provide exhaustive coverage,
but it does guide you through the most common use cases,
including:

- How to define XOS models.
- How to load the models into the `xos-core`.
- How to write a TOSCA recipe that creates an instance of the models.
- How to write a `sync_step` for the models.
- How to write unit tests for a `sync_step` (TODO).

## Prerequisites

The following assumes you start with a `minikube` deployment
of XOS (although any Kubernetes cluster will do), so that
running `kubectl get pods` returns something similar to:

```shell
NAME                             READY     STATUS    RESTARTS   AGE
xos-chameleon-6fb76d5689-s7vxb   1/1       Running   0          21h
xos-core-58bcf4f477-79hs7        1/1       Running   0          21h
xos-db-566dd8c6f9-l24h5          1/1       Running   0          21h
xos-gui-665c5f85bc-kdmbm         1/1       Running   0          21h
xos-redis-5cf77fd49f-fcw5h       1/1       Running   0          21h
xos-tosca-69588f677c-77lll       1/1       Running   0          20h
xos-ws-748c7f9f75-cnjnh          1/1       Running   0          21h
```

The tutorial also assumes you have downloaded the XOS source code
into directory `$SRC_DIR`.

> **Note:** Instructions on how to install XOS on a Kubernetes cluster
> and download the XOS source code is provided elsewhere in this Guide.

## Directory Structure

XOS services are located under `$SRC_DIR/services`. The first step
is to create a new directory to store our models and synchronizer
code. We will use the name `hello-world` for this example:

```shell
cd $SRC_DIR/services
mkdir hello-world
cd hello-world
```

Although empty when we start, we will end up with a directory
structure that looks like the following. You can look at the
corresponding directories of other services in `$SRC_DIR/services`
for examples.

```shell
hello-world
├── Dockerfile.synchronizer
├── VERSION
├── samples
│  └── hello-world.yaml
└── xos
  ├── synchronizer
  │   ├── config.yaml
  │   ├── hello-world-synchronizer.py
  │   ├── models
  │   │   └── hello-world.xproto
  │   ├── steps
  │   │   ├── sync_hello_world_service.py
  │   │   ├── sync_hello_world_service_instance.py
  │   │   ├── test_sync_hello_world_service.py
  │   │   └── test_sync_hello_world_service_instance.py
  │   └── test_config.yaml
  └── unittest.cfg
```

Walking through the structure, we see the following:

- `Dockerfile.synchronizer` specifies the Docker image we will build
   to run the synchronizer.
- `VERSION` specifies the version of our code; it is reported to the core.
- `xos/synchronizer` contains all the code that will be bundled in the
   Docker image.

Looking at some of the files, we see:

- `xos/synchronizer/models/hello-world.xproto` contains the model definitions.
- `samples/hello-world.yaml` is an example of a TOSCA recipe to instantiate those models.
- `xos/synchronizer/hello-world-synchronizer.py` is the main synchronizer process.
- `xos/synchronizer/steps/sync_hello_world_service.py` contains the
   operations needed to synchronize the backend component.

## Create the Synchronizer Entry Point

The synchronizer entry point (main looping process) is responsible for:

- loading the synchronizer configuration
- loading and running the synchronizer framework

Cut-and-paste the following into `hello-world-synchronizer.py`:

```python
import importlib
import os
import sys
from xosconfig import Config

config_file = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + '/config.yaml')
Config.init(config_file, 'synchronizer-config-schema.yaml')

observer_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),"../../synchronizers/new_base")
sys.path.append(observer_path)
mod = importlib.import_module("xos-synchronizer")
mod.main()
```

### Define the Synchronizer Configuration

In `xos/synchronizer/config.yaml` add this content:

```yaml
name: hello-world
accessor:
  username: admin@opencord.org
  password: letmein
  endpoint: xos-core:50051
models_dir: "/opt/xos/synchronizers/hello-world/models"
steps_dir: "/opt/xos/synchronizers/hello-world/steps"
required_models:
  - HelloWorldService
  - HelloWorldServiceInstance
logging:
  version: 1
  handlers:
    console:
      class: logging.StreamHandler
  loggers:
    'multistructlog':
      handlers:
          - console
      level: DEBUG
```

This tells the synchronizer framework in a running container where
to fine the configuration parameters specific to HelloWorld. By
convention, we use `/opt/xos`.

## Define Models

For our example, we are going to define the two most common models for
an XOS-managed service: `HelloWorldService` and `HelloWorldServiceInstance`.
These are HelloWorld-specific definitions of the two
[core models](../core_models.md#model-glossary):

- `Service`: defines service-wide parameters/fields.
- `ServiceInstance`:  defines subscriber-specific parameters/fields.

Open the `hello-world.xproto` file and add the following content:

```text
option name = "hello-world";
option app_label = "hello-world";

message HelloWorldService (Service){
    required string hello_from = 1 [help_text = "The name of who is saying hello", null = False, db_index = False, blank = False];
}

message HelloWorldServiceInstance (ServiceInstance){
    option owner_class_name="HelloWorldService";
    required string hello_to = 1 [help_text = "The name of who is being greeted", null = False, db_index = False, blank = False];
}
```

This specifies two models: `HelloWorldService` extends the
`Service` model, and `HelloWorldServiceInstance` extends the
`ServiceInstance` model. Both of these models inherit the
attributes defined in the parent classes, which you can see in
file `$SRC_DIR/xos-core/core/models/core.xproto`.

## Load the Models into the Core

Service models are pushed to the core through a mechanism referred to
as `dynamic onboarding` or `dynamic loading`. In practice, when a
synchronizer container runs, the first thing it does is to push its
models into the core container.

But first we need to build and deploy our synchronizer container in
the test environment.

### Build the Synchronizer Container

We assume that you are familiar with the Docker concepts of
*container* and *image*. If not, we encourage you to look here:
[Docker concepts](https://docs.docker.com/get-started/#docker-concepts)

The first thing we need to do is to define a `Dockerfile`. To
do that, open `Dockerfile.synchronizer` and add the following
content:

```text
FROM xosproject/xos-synchronizer-base:candidate

COPY xos/synchronizer /opt/xos/synchronizers/hello-world
COPY VERSION /opt/xos/synchronizers/hello-world/

ENTRYPOINT []

WORKDIR "/opt/xos/synchronizers/hello-world"

CMD bash -c "python hello-world-synchronizer.py"
```

This file is used to build our synchronizer container image. As you
might have noticed, the container image we're defining inherits
`FROM xosproject/xos-synchronizer-base:candidate`, so we'll need
to obtain that image.

We can use the following commands to do this:

```shell
eval $(minikube docker-env) # this will point our shell on the minikube docker daemon
docker pull xosproject/xos-synchronizer-base:master
docker tag xosproject/xos-synchronizer-base:master xosproject/xos-synchronizer-base:candidate
```

Now we can build our synchronizer image by executing the following
from the `$SRC_DIR/service/hello-world` directory:

```shell
eval $(minikube docker-env)
docker build -t xosproject/hello-world-synchronizer:candidate -f Dockerfile.synchronizer .
```

### Run Your Synchronizer Container

You can create a simple Kubernetes resource in a file called `kb8s-hello-world.yaml`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hello-world-synchronizer
spec:
  containers:
    - name: hello-world-synchronizer
      image: xosproject/hello-world-synchronizer:candidate
      volumeMounts:
      - name: certchain-volume
        mountPath: /usr/local/share/ca-certificates/local_certs.crt
        subPath: config/ca_cert_chain.pem
  volumes:
    - name: certchain-volume
      configMap:
        name: ca-certificates
        items:
          - key: chain
            path: config/ca_cert_chain.pem
  restartPolicy: Never
```

and then run it using `kubectl create -f kb8s-hello-world.yaml`

Check the logs of your synchronizer using:

```shell
kubetcl logs -f hello-world-synchronizer
```

You should see output similar to the following:

```text
Service version is 1.0.0.dev
required_models, found:        models=HelloWorldService, HelloWorldServiceInstance
Loading sync steps             step_dir=/opt/xos/synchronizers/hello-world/steps synchronizer_name=hello-world
Loaded sync steps              steps=[] synchronizer_name=hello-world
Skipping event engine due to no event_steps dir. synchronizer_name=hello-world
Skipping model policies thread due to no model_policies dir. synchronizer_name=hello-world
No sync steps, no policies, and no event steps. Synchronizer exiting. synchronizer_name=hello-world
```

Check that your models are on-boarded in the XOS GUI by opening the GUI:

```shell
minikube service xos-gui
```

Use the default credentials `admin@opencord.org/letmein` to login.

### Create TOSCA Recipes to Instantiate Your Models

The models you defined earlier in this tutorial are, more precisely,
model schema. Once your model schema has been loaded into the
XOS core, you can create one or more *instances* of those models.
We typically use a TOSCA recipe to do this.

The XOS TOSCA engine automatically understands workflows for any
models that have been loaded into the core. You can consult them
at any time connecting to the TOSCA endpoint from a browser:

```text
http://<minikube-ip>:30007
```

> **Note:** You can find the minikube ip by executing this command on your
> system:`minikube ip`.

In this page you should find a list of all the available resources. Just search for
`helloworldservice` and visit the corresponding page at:

```text
http://<minikube-ip>:30007/custom_type/helloworldservice
```

You will see the TOSCA definition for the `HelloWorldService` model.

You can use that (and the `HelloWorldServiceInstance` model definition
too) to create an instance of both models. For your convenience, save
the following content to a file called `hello-world-tosca.yaml`

```yaml
tosca_definitions_version: tosca_simple_yaml_1_0
imports:
  - custom_types/helloworldservice.yaml
  - custom_types/helloworldserviceinstance.yaml
  - custom_types/servicegraphconstraint.yaml

description: Create an instance of HelloWorldService and one of HelloWorldServiceInstance

topology_template:
  node_templates:

    service:
      type: tosca.nodes.HelloWorldService
      properties:
        name: HelloWorld
        hello_from: Jhon Snow

    serviceinstance:
      type: tosca.nodes.HelloWorldServiceInstance
      properties:
        name: HelloWorld Service Instance
        hello_to: Daenerys Targaryen

    constraints:
      type: tosca.nodes.ServiceGraphConstraint
      properties:
        constraints: '["HelloWorld"]'
```

This TOSCA will create an instance of your service and
an instance of your service instance.

You can then submit this TOSCA using this command:

```shell
curl -H "xos-username: admin@opencord.org" -H "xos-password: letmein" -X POST --data-binary @hello-world-tosca.yaml http://<minikube-ip>:30007/run
Created models: ['service', 'serviceinstance', 'serviceinstance']
```

Once this command has been executed, connect to the GUI at:

```shell
http://<minikube-ip>:30001
```

and see that your models have been instantiated.

> **Note:** In the home page press the `Service Instances` button to display
> `ServiceInstance` models, and the navigate to the `Hello World`
> sub-menu to the left.

## Create your First Synchronizer Steps

Everything up to this point (with the exception of defining the models
themselves) is the boilerplate needed to run a synchronizer. It is the
`sync_step` that is actually responsible for mapping changes in the
XOS data model into some action on the backend component XOS is
managing.

To keep the tutorial simple we are not going to operate on a real
component, but we can demonstrate the basic idea of how a `sync_step`
interacts with the models.

### Successful `sync_step`

Before continuing, let's remove the container we just deployed. Do
this by running:

```shell
kubectl delete pod hello-world-synchronizer
```

To write the `sync_step` we need to create two files in
`xos/synchronizer/sync_step`. The first one synchronizes the
`HelloWorldService` model and it is called
`sync_hello_world_service.py`.

Every `sync_step` extends the `SyncStep` base class, and overrides two
methods:

- `sync_record`
- `delete_record`

See the [synchronizer reference](../dev/sync_reference.md#sync-steps)
for more details.

Here is an example of `sync_step` that simply logs changes on
the `HelloWorldService` model:

```python
from synchronizers.new_base.SyncInstanceUsingAnsible import SyncStep
from synchronizers.new_base.modelaccessor import HelloWorldService

from xosconfig import Config
from multistructlog import create_logger

log = create_logger(Config().get('logging'))

class SyncHelloWorldService(SyncStep):
    provides = [HelloWorldService]

    observes = HelloWorldService

    def sync_record(self, o):
        log.info("HelloWorldService has been updated!", object=str(o), hello_from=o.hello_from)

    def delete_record(self, o):
        log.info("HelloWorldService has been deleted!", object=str(o), hello_from=o.hello_from)
```

Let's deploy this first step and see what happens. The first thing you
need to do is rebuild the synchronizer container:

```shell
eval $(minikube docker-env)
docker build -t xosproject/hello-world-synchronizer:candidate -f Dockerfile.synchronizer .
```

Once done, restart it as follows:

```shell
kubectl create -f kb8s-hello-world.yaml
```

At his point, running `kubectl logs -f hello-world-synchronizer`
should show that your synchronizer is no longer exiting, but is now
looping while waiting for changes in the models.

Every time you make a change to the model, you will see:

- The event is logged in the synchronizer log (`kubectl logs -f hello-world-synchronizer`)
- The `backend_code` and backend status of the model are updated
- The model is not picked up by the synchronizer until you make some changes to it

When you make changes to the models (you can do this via the GUI or by
updating the TOSCA you created before), you will see a message similar
to this one in the logs:

```shell
Syncing object                            model_name=HelloWorldService pk=1 synchronizer_name=hello-world thread_id=140152420452096
HelloWorldService has been updated!       hello_from=u'Jhon Snow' object=HelloWorld
Synced object                             model_name=HelloWorldService pk=1 synchronizer_name=hello-world thread_id=140152420452096
```

> **Note:** The `sync_record` method is triggered also when a model is created,
> so as soon as you start the synchronizer you will see the above message.

If you delete the model, you'll see the `delete_record` method being invoked.

### Handling Errors in a `sync_step`

We are now going to trigger an error, to demonstrate how the synchronizer
framework is going to help us in dealing with them.

Let's start creating the `sync_step` for `HelloWorldServiceInstance` 
in a file named `sync_hello_world_service.py`.

```python
from synchronizers.new_base.SyncInstanceUsingAnsible import SyncStep, DeferredException
from synchronizers.new_base.modelaccessor import HelloWorldServiceInstance

from xosconfig import Config
from multistructlog import create_logger

log = create_logger(Config().get('logging'))

class SyncHelloWorldServiceInstance(SyncStep):
    provides = [HelloWorldServiceInstance]

    observes = HelloWorldServiceInstance

    def sync_record(self, o):
        log.debug("HelloWorldServiceInstance has been updated!", object=str(o), hello_to=o.hello_to)

        if o.hello_to == "Tyrion Lannister":
          raise DeferredException("Maybe later")

        if o.hello_to == "Joffrey Baratheon":
          raise Exception("Maybe not")

        log.info("%s is saying hello to %s" % (o.owner.leaf_model.hello_from, o.hello_to))

    def delete_record(self, o):
        log.debug("HelloWorldServiceInstance has been deleted!", object=str(o), hello_to=o.hello_to)
```

To run this code you will need to:

- delete the running container
- rebuild the image
- run the container again

In this case we are emulating an error in our `sync_step`. In reality,
this can be caused by a connection error, malformed data, or any
of a number of reasons.

Go to the GUI and start playing a little bit with the models!

If you set the `HelloWorldServiceInstance.hello_to` property to `Tyrion Lannister`
you will see this keep popping up:

```shell
HelloWorldServiceInstance has been updated! hello_to=u'Tyrion Lannister' object=HelloWorld Service Instance
sync step failed!              e=DeferredException('Maybe later',) model_name=HelloWorldServiceInstance pk=1 synchronizer_name=hello-world
Traceback (most recent call last):
  File "/opt/xos/synchronizers/new_base/event_loop.py", line 357, in sync_cohort
    self.sync_record(o, log)
  File "/opt/xos/synchronizers/new_base/event_loop.py", line 227, in sync_record
    step.sync_record(o)
  File "/opt/xos/synchronizers/hello-world/steps/sync_hello_world_service_instance.py", line 18, in sync_record
    raise DeferredException("Maybe later")
DeferredException: Maybe later
```

Here is what happens when an error occurs. The synchronizer framework will:

- Log the exception
- Set the `backend_code` of that instance to `2`
- Set the `Exception` error in the `backend_status`
- Keep retrying

> **Note:** To see `backend_code` and `backend_status` in the GUI you
> can press `d` to open the debug tab while looking at a model detail view.
