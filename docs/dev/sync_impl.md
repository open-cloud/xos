# Synchronizer Implementation

There are three types of synchronizers: _Work-based_, _Event-based_, and
_Hybrid_ (the last of which subsume the functionalities of the first two).
Work-based synchronizers are somewhat cumbersome to implement, but offer strong
robustness guarantees such as causal consistency, retries in the face of
failure, model-dependency analysis and concurrent scheduling of synchronization
modules. Event-based synchronizers are simpler to implement, but lack the
aforementioned guarantees.

The current XOS Synchronizer implementation is work-based. The Synchronizer framework determines whether models are up-to-date based on examining their content, typically using timestamps embedded in the models. _Sync Steps_, also known as _Actuators_ are required to be implemented in an idempotent manner. In particular, it should not cause an error for model synchronization to occur multiple times, even if nothing has changed in the model. In the worst case, synchronizing more often than necessary is a loss of performance, not a loss of correctness.

The Synchronizer framework has facilities to assist with dependency sorting, concurrency, and error handling.

### Implementing a Work-based Synchronizer

A work-based Synchronizer is a collection of _Actuator_ modules. Each Actuator
module is invoked when a model is found to be outdated relative to its last
synchronization. An actuator module can be self-contained and written entirely
in Python, or it can be broken into a "dispatcher" and "payload", with the
dispatcher implemented in Python and the payload implemented externally using
a tool such as Ansible.

### Actuator Module API

* `Model observes`: A list of type `Model` classes that are observed by this step.

* `def sync_record(self, object)`: A method that handles outdated objects.

* `def delete_record(self, object)`" A method that handles object deletion.

* `def fetch_pending(self, deleted)`: A method that fetches the set of pending
  objects from the database. The synchronizer framework provides a default
  implementation.  Override only if you have a reason to do so.

#### Sync Steps

To implement a step, a developer need only implement the
`sync_record` and `delete_record` methods of the step, which get called for every pending
object. These methods interact directly with the underlying substrate.

There are a variety of implementations that are possible, for example calling a REST API
endpoint on an external service is a pattern that is used by many existing synchronizers.
Executing an ansible playbook is another option, and something that was done in the
past, though no current synchronizers use that pattern.

#### Managing Dependencies

If your data models have dependencies between them, so that for one to be
synchronized, another must already have been synchronized, then you can define
such dependencies in your data model. The Synchronizer automatically picks up
such dependencies and ensures that the steps corresponding to the models in
questions are executed in a valid order. It also ensures that any errors that
arise propagate from the affected objects to its dependents, and that the
dependents are held up until the errors have been resolved and the dependencies
have been successfully synchronized.  In the absence of failures, the
Synchronizer tries to execute your synchronization steps concurrently to
whatever extent this is possible while still honoring dependencies.

Dependencies are typically specified in a model-deps file that has a simple
json-based syntax. For example,

```json
{
    "User": [
        ["Site", "site", "users"],
    ]
}
```

In the example above, this specifies that the `User` model depends on the `Site` model, and
that these two models are linked by the fields `site` (in the `User` model) and `users` (in
the `Site` model).

#### Handling Errors

To fault synchronization, you can raise an exception in any of the methods of
your step that are automatically called by the synchronizer core. These include
`fetch_pending`, `sync_record` and `delete_record`. The outcome of such
exceptions has multiple parts:

1. The synchronization of the present object is deferred.

2. The synchronization of dependent objects is deferred, if those objects are
   accessible via the current object (see the `via` field).

3. A string representation of your exception is propagated into a scratchpad in
   your model, which in turn appears in your UI. When you click the object in
   question, in the UI, you should see the error message.

4. The synchronization state of your object, and of dependent objects changes
   to "Error" and a red icon appears next to it.

5. If the object repeatedly fails to synchronize, then its synchronization
   interval is increased exponentially.

Sometimes, you may encounter a temporary error, which you think may be resolved
shortly, by the time the Synchronizer runs again. In these cases, you can raise
a `DeferredException`. This error type differs from a general exception in two
ways:

1. It does not put your object in error state.

2. It disables exponential backoff (i.e., the Synchronizer tries to synchronize
   your object every single time).

### Responding to external activity

The original purpose of the Synchronizer framework was to implement top-down control flow, but it
was quickly discovered a Synchronizer is a convenient place to implement bottom-up feedback flow.
To do this, a few new classes of steps were implemented.

#### Event Steps

Event steps allow external events to update state in the data model. Event steps typically use
`Kafka` as an event bus, registering on a specific `topic`. When messages on the `topic` arrive,
a method in the event step, `process_event` is called with the contents of the event. The event step
is then free to use the API to modify, delete, or create models as necessary.

#### Pull Steps

Pull steps are similar to event steps, but use a polling mechanism instead of an event mechanism.
Pull steps must implement a method called `pull_records`. This method is called periodically and
allows the step to conduct any polling that is necessary. The step is then free to alter the data
model.

### Implementing model-to-model policies

`model_polices` are yet another type of step. Rather than performing top-down control flow
or bottom-up feedback flow, a `model_policy` implements a sideways action, a place for
changes in one model to cause changes in another. For example, "When object A is created,
also create object B and link it to object A" is one common policy pattern.

`model_policies` must declare a `model_name` that the policy will operate on. After that,
the policy will declare a set of handlers,

* `handle_create(obj)`. Called whenever an object is created.
* `handle_update(obj)`. Called whenever an object is modified.
* `handle_delete(obj)`. Called whenever an object is deleted.

### Synchronizer Configuration Options

The following table summarizes the available configuration options. For
historical reasons, they are called `observer_foo` since Synchronizers were
called Observers in an earlier version of XOS.

|    Option    |   Default    |     Purpose     |
|---------|----------|-----------|
| `name` |  N/A  |  The name of the synchronizer |
| `accessor` |  N/A  |  A subsection of the config file that describes the `username`, `password`, and `endpoint` to contact the XOS core. |
| `core_version` |  N/A  |  Specifies the version of the core that is required by this synchronizer. |
| `dependency_graph` | `/opt/xos/model-deps` | Dependencies between various models that your Synchronizer services. These may be generated manually or generated automatically using `xosgenx` |
| `models_dir` | N/A | The directory in which model xproto is stored.|
| `steps_dir`  | N/A  | The path of the directory in which the Synchronizer will look for your actuator modules. |
| `model_policies_dir` | N/A | The directory in which model policies are stored.|
| `pull_steps_dir` | N/A | The directory in which pull steps are stored.|
| `event_steps_dir` | N/A | The directory in which event steps are stored.|
| `event_bus` |  N/A  |  A subsection that describes the kafka endpoint used by the Event steps. Has two required fields, `kind` which must be set to `kafka` and `endpoint` which is the endpoint.|
| `logging` | N/A | A section that describe logging settings.|

