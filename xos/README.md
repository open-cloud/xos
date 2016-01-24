## XOS Source Tree

This is the main directory for XOS. Sub-directories include:

* configurations -- collection of canned configurations
* core -- core model definitions
* generators -- tools to generate auxiliary structures from data model
* model_policies -- invariants on the data model
* nginx, uwsgi -- related to web server that runs XOS
* openstack -- client-side interaction with OpenStack (to be depreciated)
* services -- model definitions for a set of services
* synchronizers -- collection of synchronizers
* templates -- Django GUI templates
* test -- system-wide tests to be collected here
* tosca -- tosca modeling layer on top of RESTful API
* tools -- assorted tools and scripts
* xos -- common source code for all Django applications
* xos_configuration -- top-level XOS configuration parameters

Of these, configuration, services, and synchronizers are most
relevant to developers.
