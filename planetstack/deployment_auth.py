## 
# This file contains the auth credentials used to access openstack deployments 
# we wish to manage. The 'default' credentials will be used for any deployments
# not specifed here.
#

deployment_auth = {
# Example
#   'deployment_name': {
#       'user': 'email@domain.com',
#       'pasword': 'password',
#       'tenant': 'tenant',    
#       'url': 'http://localhost:5000/v2.0/',
#       'token': 'ADMIN',
#       'endpoint': 'http://localhost:35357/v2.0/'    
#    }, 
    
    'default': {
        'user': 'admin@domain.com',
        'password': 'admin',
        'tenant': 'admin', 
        'url': 'http://localhost:5000/v2.0/'     
    },

}
