# Synchronizer Design

Synchronizers act as the link between the data model and the functional half of
the system. The data model contains a clean, abstract and declarative
representation of the system curated by service developers and operators. This
representation is not subject to the idiosyncrasies of distributed system
behavior. It defines the authoritative state of the system. The functional half
of the system, on the other hand, consists of the software that implements
services along with the resources on which they run. Unlike the data model, its
configuration is error-prone, liable to reach anomalous states, and involves
mechanisms whose implementation and management sometimes do not follow best
practices.

A Synchronizer bridges these two sides of the system robustly through the use
of an approach we call “goal-oriented synchronization.” Rather than tracking
and relaying changes from the data model to the back-end system in the form of
events, a synchronizer tracks and drives the system towards a final “goal
state” corresponding to the current state defined by the data model. And it
does so irrespective of the particular combination of changes that led to that
state. As a consequence, an opportunity is made available at every step of
synchronization to correct for anomalies created by prior steps, or ones that
arise due to ambient system activity.

The specific method we use to accomplish this property is to require
synchronization actions to be idempotent. This requirement boils down to two
constraints on the implementation of a synchronizer. The first is for a
synchronizer to compute a delta between the current and desired state of the
service component it manages, and to then apply that delta. The second is to
ensure that changes can never propagate back from the synchronizer to the data
model in a way that affects the Synchronizer’s behavior. Of these, the first
requirement is a burden on the service developer who implements a particular
synchronizer, and the second requirement is fulfilled by the synchronizer core,
which all service synchronizers share. The specific details of how the flow of
details is kept unidirectional are provided in detail in later sections. For
now, we will introduce the actors in a synchronizer that interact with the data
model.

## Actors and Types of State

There are four actors in a Synchronizer that interact with a Data Model:

* **Synchronizer Actuators:** An actuator is notified of changes to the data
  model, upon which it refers to the current state of its service in the data
  model, and idempotently translates it into a configuration for that service.
  A given data model can only have one actuator, scheduled by the synchronizer
  core in an ordering consistent with the dependencies on the model that it
  synchronizes, with possible retries and error management.

* **Model Policies:** A model policy encapsulates data relationships between
  related data models, such as “for every Network there must be at least one
  interface.” Concretely in this example, a model policy would intercept
  creations of Network models and create Interface models accordingly.

* **Event Steps:** Event steps listen for external events and update the
  data model.

* **Pull Steps:** Pull steps poll external components for state and update
  the data model.

The Data Model represents the authoritative and abstract state of the system.
By authoritative, we mean that if there is a conflict, then it is given
precedence over the internal configuration of services. This state is a
combination of two types of fields:

* **Declarative:** Declarative state is sufficient to recreate the full
  operational state of the system, with the help of a particular synchronizer.

* **Feedback:** Feedback state is derivative. It is the result of Synchronizer
  actions, preserved as a cache for later accesses to the backend objects
  created as a consequence of those actions.

Synchronizers are mainly interested in declarative state, as that is the basis
on which they configure the service they implement. The core synchronizer
machinery ensures that synchronizers are notified of changes to declarative
state, that they are invoked in an appropriate order, and also provide a degree
of resilience to failure.

The actors of a synchronizer interact with this state in the following manner:

* Actuators can:
    * Read Declarative state
    * Read/Write Feedback state
    * Be scheduled upon changes to Declarative state

* Model Policies can
    * Read/Write Declarative state
    * Subscribe to changes to Declarative state

* Event Steps and Pull Steps can
    * Read/Write Declarative state
    * Read/Write Feedback state

## Relationships Between Synchronizers and Models

A single synchronizer can synchronize multiple data models, usually through an
actuator per model. However, a given model can only be handled by one actuator.
Furthermore, a single actuator only synchronizes one data model. The act of
synchronizing may generate feedback state in the same model, but watching never
generates/modifies feedback state in the model being watched. (Watching model A
may be part of synchronizing mode B, and so generates feedback state in B.)

But how are these relationships established? The answer lies in the linkages
between models in the data model. The data model, which is implemented using
Django, lets us link one model to another through references called foreign
keys and many-to-many keys. Apart from enabling organizational patterns such as
aggregation, composition, proxies, etc. this linkage is used to establish two
levels of dependencies: ones between models, and ones between objects. If a
field interface in a model for a daemon references an Interface model, then it
implies that the daemon’s model depends on interface. Furthermore, that an
object of type daemon depends on an object of type interface if the interface
field of the latter contains a reference to the latter.

Dependencies between models can be specified in two ways:

* Implicitly through linkages in the data model
* Explicitly through annotations, which are in turn read by the synchronizer
  core

Once these dependencies have been extracted, they configure the scheduling
of actuators in a way that they are run in dependency order, and so that errors
in the execution of an actuator are propagated to its dependencies. Consider
the diagram below.

## Loops

The separation of declarative and feedback state in the data model eliminates
the possibility of loops involving actions, caused by a synchronizer directly
modifying its declarative state. Such loops involve repeated executions of one
or more actions by the synchronizer core. But it does not eliminate loops of
the following kind

1. Loops caused because a synchronizer modifies declarative state indirectly -
   say by triggering an external action that modifies the state via the API.

2. Loops in which feedback state written by one Synchronizer is read
   by a second Synchronizer, and feedback state written by the second
   Synchronizer is read by the first Synchronizer. Of course, this
   type of interference can also happen across a chain of Synchronizers.

3. Spin loops and other general loops found in programs.

The second possibility is unlikely in practice because it would be akin to a
data model version of a layering violation: Layer _i_ depends on Layer _i+1_,
while at the same time Layer _i+1_ would depend on Layer _i_.

## Dependencies and Data Consistency

XOS enforces sequential consistency, without real-time bounds. This is to say
that no guarantees are made on when the goal state will be transferred from the
data model to the back end, but it is guaranteed that the components of the
states defined by individual data models will be actuated in a valid order.
This order is implied by the dependencies described in the previous section.
For example, if a host model depends on an interface model, then it is
guaranteed that the actuator of a host will execute only when the actuator of
the corresponding interface has completed successfully.

Outside of the ordering mandated by dependencies in the data model, operations
may be rearranged randomly, or to favor the concurrent scheduling of actuators.
This property poses an important task for a service designer, making it
necessary for him to specify all ordering constraints comprehensively in the
service data model. If any orderings are missed, then even if changes to a set
of models are properly ordered at the source, their actuation may be reordered
into sequences that are invalid.

## Error Handling and Idempotence

The synchronizer is designed to be robust to unforeseeable faults in the
back-end system. The main source of this robustness is the idempotence of
actuators. Rather than blindly executing an operation on the current state,
actuators target a goal state. This means that they are expected to make a
reasonable effort to compensate for anomalies. Goal-directed synchronization,
i.e., the strategy of driving towards the end state, rather than simply
“replaying” events is central to this outcome. In the latter case, actuators
would have no other choice than to dutifully apply incoming updates, even if
the start state is anomalous, and likely lead to an anomalous end state.

A synchronizer tries to schedule as many actuators as it can concurrently
without violating dependencies. Dependencies are tracked at the object level.
For example, in the example mentioned previously, the failure of the
synchronization of an interface would hold up a host if the interface is bound
to it, but not if that interface is bound to a different node. When there is a
failure, the synchronizer core re-executes the actuator at a later time, and
then again at increasing intervals.

## Timestamps

XOS models come with a variety of timestamps. The first three timestamps indicate changes that occur to the models:

* `Updated`. Updated is set whenever a model is saved by a non-synchronizer. For example, updating a model via the GUI or the REST API will cause the updated timestamp to be set. The updated timestamp is set regardless of whether or not any actual changes have occurred to the model. This allows a developer or operator to save a model and cause the model to be resynchronized.

* `changed_by_step`. This timestamp is set whenever non-bookkeeping fields in the model are changed during the execution of a syncstep. If no changes occur during a save, then this timestamp is not set.

* `changed_by_policy`. This timestamp is set whenever non-bookkeeping fields in the model are changed during the execution of a model policy. If no changes occur during a save, then this timestamp is not set.

For a given model, if we take the maximum of the three timestamps, `max(model.updated, model.changed_by_step, model.changed.by_policy)`, we can use that calculation as an overall version of the substantive fields of the model. If a user updated the model, or if a policy or syncstep changed the model, then one of those timestamps will be updated.

The following two timestamps are set when a sync or a model_policy is completed.

* `enacted`. Enacted indicates the model has been successfully synced. It is set to `max(model.updated, model.changed_by_policy)`. The enacted timestamp does not indicate the time of the synchronization, but rather indicates the version of the data that was synchronized.

* `policed`. Policed indicates the model has successfully had model policies applied. It is set to `max(model.updated, model.changed_by_step)`. The policed timestamp does not indicate the time the policy completed, but rather indicates the version of the data that had policies applied.

The rules for running steps and policies are as follows:

* Model policies are run if `model.updated > model.policed || model.changed_by_step > model.policed`. In other words, if a user updates the model, or a syncstep changes the model, then policies will run.

* Sync steps are run if `model.udpated > model.enacted || model.changed_by_policy > model.enacted`. In other words, if a user updates the model, or a policy changes the model, then steps will be run.

This means it is possible for a syncstep to trigger a policy, and it is possible for a policy to trigger a syncstep. A cycle is not necessarily bad assuming the cycle does eventually terminate in a steady state. Because the `changed_by_` timestamps are only set when a model changes (i.e. authoritative state change), and not merely when it is saved, simply no longer making changes to a model will break any cycle. It's recommended that developers do exercise caution when modifying models from both syncsteps and policies.
