# Writing Synchronizers

Synchronizers are the components of CORD that map the abstract
declarative state about how the system is suppose to behave (as defined by the
XOS data model) into the concrete operational state of the backend components
that implement the system (e.g., VNFs, micro-services, SDN control
applications).

Writing a Synchronizer is half of the work required to on-board a service into
CORD. First a model for the service is written as an [xproto](xproto.md)
specification, and then you implement a synchronizer that translates that model
onto some backend component.

To implement a Synchronizer, it is important to first understand the role they
play in CORD and the assumptions made about their behavior. The next section
describes a set of [design guidelines](sync_arch.md) and the following one
presents the [implementation details](sync_impl.md).

