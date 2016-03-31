## XOS REST API

The XOS API importer is automatic and will search this subdirectory and its hierarchy of children for valid API methods. API methods that are descendents of the django View class are discovered automatically. This should include django_rest_framework based Views and Viewsets. This processing is handled by import_methods.py.

A convention is established for locating API methods within the XOS hierarchy. The root of the api will automatically be /api/. Under that are the following paths:

* `/api/service` ... API endpoints that are service-wide
* `/api/tenant` ... API endpoints that are relative to a tenant within a service

For example, `/api/tenant/cord/subscriber/` contains the Subscriber API for the CORD service. 

The API importer will automatically construct REST paths based on where files are placed within the directory hierarchy. For example, the files in `xos/api/tenant/cord/` will automatically appear at the API endpoint `http://server_name/api/tenant/cord/`. 
The directory `examples` contains examples that demonstrate using the API from the Linux command line.
