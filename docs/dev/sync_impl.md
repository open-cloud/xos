## Implementation Details 

There are three types of synchronizers: _Work-based_, _Event-based_, and _Hybrid_ (the last of which subsume the functionalities of the first two). Work-based synchronizers are somewhat cumbersome to implement, but offer strong robustness guarantees such as causal consistency, retries in the face of failure, model-dependency analysis and concurrent scheduling of synchronization modules. Event-based synchronizers are simpler to implement, but lack the aforementioned guarantees. 

### Differences between Work-based and Event-based Synchronizers 

|   Mechanism   |   Work-Based Synchronizers   |   Event-based Synchronizers   |
|--------------------|------------------------------------------|------------------------------------------|
| Control-logic binding | Check if models are up-to-date based on their content | React to events notifying of model updates |
| Implementation constraints | Modules have to be idempotent | Modules are not required to be idempotent |
| Dependencies | Modules are executed in dependency order | Modules are executed reactively in an arbitrary order |
| Concurrency | Non-dependent modules are executed concurrently | Modules are executed sequentially |
| Error handling | Errors are propagated to dependencies; retries on failure | No error dependency; it’s up to the Synchronizer to cope with event loss |
| Ease of implementation | Moderate | Easy |
 
### Implementing an Event-based Synchronizer 

An Event-based Synchronizer is a collection of _Watcher_ modules. Each Watcher module listens for (i.e., watches) events pertaining to a particular model. The Synchronizer developer must provide the set of these modules. The steps for assembling a synchronizer once these modules have been implemented, are as follows:

1. Run the generate watcher script: `gen_watcher.py <name of your app>`

2. Set your Synchronizer-specific config options in the config file, and also set `observer_enable_watchers` to true. 

3. Install python-redis by running `pip install redis` in your Synchronizer container 

4. Link the redis container that comes packaged with XOS with your Synchronizer container as `redis`. 

5. Drop your watcher modules in the directory `/opt/xos/synchronizers/<your synchronizer>/steps`

6. Run your synchronizer by running `/opt/xos/synchronizers/<your synchronizer>/run-synchronizer.sh`

### Watcher Module API 

* `def handle_watched_object(self, o)`: A method, called every time a watched object is added, deleted, or updated. 

* `int watch_degree`: A variable of type `int` that defines the set of watched models _implicitly_. If this module synchronizes models A and B, then the watched set is defined by the models that are a distance `watch_degree` from A or from B in the model dependency graph. 

* `ModelLink watched`: A list of type `ModelLink` that defines the set of watched models _explicitly_. If this is defined, then `watch_degree` is ignored. 

* `Model synchronizes`: A list of type `Model` that identifies the model that this  module synchronizes. 

The main body of a watcher module is the function `handle_watched_object`, which responds to operations on objects that the module synchronizes. If the module responds to multiple object types, then it must determine the type of object, and proceed to process it accordingly. 
 
```python 
def handle_watched_object(self, o):
    if (type(o) is Slice):
        self.handle_changed_slice(o) 
    elif (type(o) is Node):
        self.handle_changed_node(o) 
```

#### Linking the Watcher into the Synchronizer 

There are two ways of linking in a Watcher. Using them both does not hurt. The first method is complex but robust, and involves making the declaration in the data model, by ensuring that the model that your synchronizer would like to watch is linked to the model that it actuates. For instance, if your synchronizer actuates a service model called Fabric, which links the Instance model, then you would ensure that Instance is a dependency of Fabric by making the following annotation in the Fabric model:

```python 
class Fabric(Service):
    ... 
    ... 
    xos_links = [ModelLink(Instance,via='instance',into='ip')]
```
	
There can be several `ModelLink` specifications in a single `xos_links` declaration, each encapsulating the referenced model, the field in the current model that links to it, and the destination field in which the watcher is interested. If into is omitted, then the watcher is notified of all changes in the linked model, irrespective of the fields that change. 
	
The above change needs to be backed up with an instruction to the synchronizer that the watcher is interested in being notified of changes to its dependencies. This is done through a `watch_degree` annotation. 
	
```python 
class SyncFabricService(SyncStep):
   watch_degree=1 
```

By default, `watch_degree = 0`, means the Synchronizer watches nothing. When watch degree is 1, it watches one level of dependencies removed, and so on. If the `watch_degree` in the above code were 2, then this module would also get notified of changes in dependencies of the `Instance` model. 

The second way of linking in a watcher is to hardcode the watched model directly in the synchronizer:

```python 
class SyncFabricService(SyncStep):
    watched = [ModelLink(Instance,via='instance',into='ip')]
```

#### Linking the Watcher into the Synchronizer 

* Set the `observer_enable_watchers` option to true in your XOS synchronizer config file. 

* Add a link between your synchronizer container and the redis container by including the following lines in the definition of your synchronizer's docker-compose file. You may need to adapt these to the name of the project used (e.g. cordpod) 

  - `external_links:`
       - `xos_redis:redis`

* Ensure that there is a similar link between your XOS UI container and the redis container. 

In addition to the above development tasks, you also need to make the following changes to your configuration to activate watchers. 

### Implementing a Work-based Synchronizer 

A work-based Synchronizer is a collection of _Actuator_ modules. Each Actuator module is invoked when a model is found to be outdated relative to its last synchronization. An actuator module can be self-contained and written entirely in Python, or it can be broken into a "dispatcher" and "payload", with the dispatcher implemented in Python and the payload implemented using Ansible. The Synchronizer core has built-in support for the dispatch of Ansible modules and helps extract parameters from the synchronized model and translate them into the parameters required by the corresponding Ansible script. It also tracks an hierarchically structured list of such ansible scripts on the filesystem, for operators to use to inspect and debug a system. The procedure for building a work-based synchronizer is as follows:

1. Run the gen_workbased.py script. gen_workbased <app name>. 

2. Set your Synchronizer-specific config options in the config file, and also set observer_enable_watchers to False. 

3. Drop your actuator modules in the directory `/opt/xos/synchronizers/<your synchronizer>/steps`

4. Run your synchronizer by running `/opt/xos/synchronizers/<your synchronizer>/run-synchronizer.sh`

### Actuator Module API 

* `Model synchronizes`: A list of type `Model` that records the set of models that the module synchronizes. 

* `def sync_record(self, object)`: A method that handles outdated objects. 

* `def delete_record(self, object)`" A method that handles object delection. 

* `def get_extra_attributes(self, object)`: A method that maps an object to 
the parameters required by its Ansible payload. Returns a `dict` with those 
parameters and their values. 

* `def fetch_pending(self, deleted)`: A method that fetches the set of pending 
objects from the database. The synchronizer core provides a default implementation. 
Override only if you have a reason to do so. 

* `string template_name`: The name of the Ansible script that directly interacts 
with the underlying substrate. 

#### Implementing a Step with Ansible 

To implement a step using Ansible, a developer must provide two things: an Ansible recipe, and a `get_extra_attributes` method, which maps attributes of the object into a dictionary that configures that Ansible recipe. The Ansible recipe comes in two parts, an inner payload and a wrapper that delivers that payload to the VMs associated with the service. The wrapper itself comes in two parts. A part that sets up the preliminaries:
 
 ```python 

---
 
- hosts: "{{ instance_name }}"
  connection: ssh 
  user: ubuntu 
  sudo: yes 
  gather_facts: no 
  vars:
    - package_location: "{{ package_location }}"
    - server_port: "{{ server_port }}"
```

The template variables `package_location` and `server_port`
come out of the Python part of the Synchronizer implementation 
(discussed below). The outer wrapper then includes a set of Ansible 
roles that perform the required actions:

```python 
roles:
  - download_packages 
  - configure_packages 
  - start_server 
```

 The "payload" of the Ansible recipe contains an implementation 
 of the roles, in this case, `download_packages`, `configure_packages`,
 and `start_server`. The concrete values of parameters required by the 
 Ansible payload are provided in the implementation of the `get_extra_attributes`
 method in the Python part of the Synchronizer. This method receives an object 
 from the data model and is charged with the task of converting the properties of 
 that object into the set of properties required by the Ansible recipe, which are 
 returned as a Python dictionary. 
 
```python 
def get_extra_attributes(self, o):
        fields = {}
        fields['package_location'] = o.package_location 
        fields['server_port'] = o.server_port 
        return fields 
```

#### Implementing a Step without Ansible 

To implement a step without using Ansible, a developer need only implement the `sync_record` and `delete_record` methods, which get called for every pending 
object. These methods interact directly with the underlying substrate. 

#### Managing Dependencies 

If your data models have dependencies between them, so that for one to be synchronized, another must already have been synchronized, then you can define such dependencies in your data model. The Synchronizer automatically picks up such dependencies and ensures that the steps corresponding to the models in questions are executed in a valid order. It also ensures that any errors that arise propagate from the affected objects to its dependents, and that the dependents are held up until the errors have been resolved and the dependencies have been successfully synchronized. 
In the absence of failures, the Synchronizer tries to execute your synchronization steps concurrently to whatever extent this is possible while still honoring dependencies. 

```python 
<in the definition of your model>
xos_links = [ModelLink(dest=MyServiceUser,via='user'),ModelLink(dest=MyServiceDevice,via='device') ]
```

In the above example, the `xos_links` field declares two dependencies. The name `xos_links` is key, and so the field should be named as such. The dependencies are contained in a list of type `ModelLink`, each of which defines a type of object (a model) and an "accessor" field via which a related object of that type can be accessed. 

#### Handling Errors 

To fault synchronization, you can raise an exception in any of the methods of your step that are automatically called by the synchronizer core. These include `fetch_pending`, `sync_record` and `delete_record`. The outcome of such exceptions has multiple parts:

1. The synchronization of the present object is deferred. 

2. The synchronization of dependent objects is deferred, if those objects are accessible via the current object (see the `via` field). 

3. A string representation of your exception is propagated into a scratchpad in your model, which in turn appears in your UI. When you click the object in question, in the UI, you should see the error message. 

4. The synchronization state of your object, and of dependent objects changes to "Error" and a red icon appears next to it. 

5. If the object repeatedly fails to synchronize, then its synchronization interval is increased exponentially. 

Sometimes, you may encounter a temporary error, which you think may be resolved shortly, by the time the Synchronizer runs again. In these cases, you can raise a `DeferredException`. This error type differs from a general exception in two ways:

1. It does not put your object in error state. 

2. It disables exponential backoff (i.e., the Synchronizer tries to synchronize your object every single time). 

#### Synchronizer Configuration Options 

The following table summarizes the available configuration options. For historical reasons, they are called `observer_foo` since Synchronizers were called Observers in an earlier version of XOS. 

|    Option    |   Default    |     Purpose     |
|---------|----------|-----------|
| `observer_disabled` |  False  |  A directive to run without synchronizing. Events are not relayed to the Synchronizer and no bookkeeping is done. |
| `observer_steps_dir`  | N/A  | The path of the directory in which the Synchronizer will look for your watcher and actuator modules. |
| `observer_sys_dir` | N/A | The path of the directory that enlists backend objects your synchronizer creates. This is like the `/sys` directory in an operating system. Each entry is a file that contains an Ansible recipe that creates, updates or deletes your object. When you debug your synchronizer, you can run these files manually. |
| `observer_pretend` | False | This option runs the Synchronizer in "pretend" mode, in which synchronizer modules that use Ansible run in emulated mode, and do not actually execute backend API calls. |
| `observer_proxy_ssh` |  N/A |    |
| `observer_name` | N/A | The name of your Synchronizer. This is a required option. |
| `observer_applist` | core | A list consisting of the Django apps that your Synchronizer uses. |
| `observer_dependency_graph` | `/opt/xos/model-deps` | Dependencies between various models that your Synchronizer services. These are generated automatically by the Synchronizer utility `dmdot`. |
| `observer_backoff_disabled` | True | Models whose synchronization fails are re-executed, but with intervals that increase exponentially. This option disables the exponential growth of the intervals. |
| `observer_logstash_hostport` | N/A | The host name and port number (e.g. `xosmonitor.org:4132`) to which the Synchronizer streams its logs, on which a logstash server is running. |
| `observer_log_file~ | N/A | The log file into which the Synchronizer logs are published. |
| `observer_model_policies_dir` | N/A | The directory in which model policies are stored.|
