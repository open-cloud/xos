## XOS Source Tree

This is the main directory for XOS. Sub-directories include:

* configurations -- deprecated (configurations have moved to the `service-profile` repository)
* core -- core model definitions
* generators -- tools to generate auxiliary structures from data model
* model_policies -- invariants on the data model
* nginx, uwsgi -- related to web server that runs XOS
* openstack -- client-side interaction with OpenStack (to be depreciated)
* services -- now auto-populated by the XOS service on-boarding process
* synchronizers -- shared synchronizer framework (plus legacy sychnronizers)
* templates -- Django GUI templates
* test -- system-wide tests to be collected here
* tosca -- tosca modeling layer on top of RESTful API
* tools -- assorted tools and scripts
* xos -- common source code for all Django applications
* xos_configuration -- top-level XOS configuration parameters

Individual services now live in their own (peer) repository, and XOS
configuration parameters -- including the service graph to be
on-boarded into a given deployment -- live in the `service-profile`
repository.
