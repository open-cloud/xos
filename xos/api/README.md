## XOS REST API

Source for the XOS REST API lives in directory `xos/api`. An importer
tool, `import_methods.py`, auto-generates the REST API by searching
this directory (and sub-directories) for valid API methods. These
methods are descendents of the Django View class. This should include
django_rest_framework based Views and Viewsets.

We establish a convention for locating API methods within the XOS
hierarchy. The root of the api is automatically `/api/`. Under that
are the following paths:

* `/api/service` ... API endpoints that are service-wide
* `/api/tenant` ... API endpoints that are relative to a tenant within a service

For example, `/api/tenant/cord/subscriber/` contains the Subscriber
API for the CORD service.

The API importer automatically constructs REST paths based on
where files are placed within the directory hierarchy. For example,
the files in `xos/api/tenant/cord/` will automatically appear at the
API endpoint `http://server_name/api/tenant/cord/`.  The directory
`examples` contains examples that demonstrate using the API from the
Linux command line.
