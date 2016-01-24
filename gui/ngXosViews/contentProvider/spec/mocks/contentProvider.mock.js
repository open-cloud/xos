/* eslint-disable key-spacing, no-unused-vars */

var CPmock = {
  CPlist: [
    {
      'humanReadableName':'on_lab_content',
      'validators':{
        'updated':[

        ],
        'policed':[

        ],
        'name':[
          'notBlank'
        ],
        'created':[

        ],
        'deleted':[

        ],
        'serviceProvider':[
          'notBlank'
        ],
        'description':[

        ],
        'enabled':[

        ],
        'lazy_blocked':[

        ],
        'backend_register':[
          'notBlank'
        ],
        'write_protect':[

        ],
        'content_provider_id':[

        ],
        'backend_status':[
          'notBlank'
        ],
        'id':[

        ],
        'no_sync':[

        ],
        'enacted':[

        ]
      },
      'id':1,
      'created':'2015-10-22T19:33:55.078Z',
      'updated':'2015-10-22T19:33:55.078Z',
      'enacted':null,
      'policed':null,
      'backend_register':'{}',
      'backend_status':'0 - Provisioning in progress',
      'deleted':false,
      'write_protect':false,
      'lazy_blocked':false,
      'no_sync':false,
      'content_provider_id':null,
      'name':'on_lab_content',
      'enabled':true,
      'description':null,
      users: [2],
      'serviceProvider':'http://0.0.0.0:9000/hpcapi/serviceproviders/1/'
    },
    {
      'humanReadableName':'test',
      'validators':{
        'updated':[

        ],
        'policed':[

        ],
        'name':[
          'notBlank'
        ],
        'created':[

        ],
        'deleted':[

        ],
        'serviceProvider':[
          'notBlank'
        ],
        'description':[

        ],
        'enabled':[

        ],
        'lazy_blocked':[

        ],
        'backend_register':[
          'notBlank'
        ],
        'write_protect':[

        ],
        'content_provider_id':[

        ],
        'backend_status':[
          'notBlank'
        ],
        'id':[

        ],
        'no_sync':[

        ],
        'enacted':[

        ]
      },
      'id':2,
      'created':'2015-10-23T10:50:37.482Z',
      'updated':'2015-10-23T10:52:56.232Z',
      'enacted':null,
      'policed':null,
      'backend_register':'{}',
      'backend_status':'0 - Provisioning in progress',
      'deleted':false,
      'write_protect':false,
      'lazy_blocked':false,
      'no_sync':false,
      'content_provider_id':null,
      'name':'test',
      'enabled':true,
      'description':'',
      'serviceProvider':'http://0.0.0.0:9000/hpcapi/serviceproviders/1/'
    }
  ],
  SPlist: [
    {
      'humanReadableName':'main_service_provider',
      'validators':{
        'updated':[

        ],
        'policed':[

        ],
        'name':[
          'notBlank'
        ],
        'created':[

        ],
        'deleted':[

        ],
        'hpcService':[
          'notBlank'
        ],
        'description':[

        ],
        'enabled':[

        ],
        'service_provider_id':[

        ],
        'lazy_blocked':[

        ],
        'backend_register':[
          'notBlank'
        ],
        'write_protect':[

        ],
        'backend_status':[
          'notBlank'
        ],
        'id':[

        ],
        'no_sync':[

        ],
        'enacted':[

        ]
      },
      'id':1,
      'created':'2015-10-22T19:33:55.048Z',
      'updated':'2015-10-22T19:33:55.048Z',
      'enacted':null,
      'policed':null,
      'backend_register':'{}',
      'backend_status':'0 - Provisioning in progress',
      'deleted':false,
      'write_protect':false,
      'lazy_blocked':false,
      'no_sync':false,
      'hpcService':'http://0.0.0.0:9000/hpcapi/hpcservices/1/',
      'service_provider_id':null,
      'name':'main_service_provider',
      'description':null,
      'enabled':true
    }
  ],
  CDNlist: [
    {
      'humanReadableName':'onlab.vicci.org',
      'validators':{
        'updated':[

        ],
        'contentProvider':[
          'notBlank'
        ],
        'policed':[

        ],
        'created':[

        ],
        'deleted':[

        ],
        'description':[

        ],
        'enabled':[

        ],
        'cdn_prefix_id':[

        ],
        'lazy_blocked':[

        ],
        'backend_register':[
          'notBlank'
        ],
        'write_protect':[

        ],
        'prefix':[
          'notBlank'
        ],
        'defaultOriginServer':[

        ],
        'backend_status':[
          'notBlank'
        ],
        'id':[

        ],
        'no_sync':[

        ],
        'enacted':[

        ]
      },
      'id':5,
      'created':'2015-10-26T13:09:44.343Z',
      'updated':'2015-10-26T13:09:44.343Z',
      'enacted':null,
      'policed':null,
      'backend_register':'{}',
      'backend_status':'0 - Provisioning in progress',
      'deleted':false,
      'write_protect':false,
      'lazy_blocked':false,
      'no_sync':false,
      'cdn_prefix_id':null,
      'prefix':'onlab.vicci.org',
      'contentProvider':1,
      'description':null,
      'defaultOriginServer':'http://0.0.0.0:9000/hpcapi/originservers/2/',
      'enabled':true
    },
    {
      'humanReadableName':'downloads.onosproject.org',
      'validators':{
        'updated':[

        ],
        'contentProvider':[
          'notBlank'
        ],
        'policed':[

        ],
        'created':[

        ],
        'deleted':[

        ],
        'description':[

        ],
        'enabled':[

        ],
        'cdn_prefix_id':[

        ],
        'lazy_blocked':[

        ],
        'backend_register':[
          'notBlank'
        ],
        'write_protect':[

        ],
        'prefix':[
          'notBlank'
        ],
        'defaultOriginServer':[

        ],
        'backend_status':[
          'notBlank'
        ],
        'id':[

        ],
        'no_sync':[

        ],
        'enacted':[

        ]
      },
      'id':1,
      'created':'2015-10-26T13:09:44.196Z',
      'updated':'2015-10-26T13:09:44.196Z',
      'enacted':null,
      'policed':null,
      'backend_register':'{}',
      'backend_status':'0 - Provisioning in progress',
      'deleted':false,
      'write_protect':false,
      'lazy_blocked':false,
      'no_sync':false,
      'cdn_prefix_id':null,
      'prefix':'downloads.onosproject.org',
      'contentProvider':2,
      'description':null,
      'defaultOriginServer':'http://0.0.0.0:9000/hpcapi/originservers/1/',
      'enabled':true
    }
  ],
  OSlist: [
    {
      'humanReadableName':'another.it',
      'validators':{
        'updated':[

        ],
        'contentProvider':[
          'notBlank'
        ],
        'origin_server_id':[

        ],
        'policed':[

        ],
        'created':[

        ],
        'deleted':[

        ],
        'description':[

        ],
        'enabled':[

        ],
        'redirects':[

        ],
        'protocol':[
          'notBlank'
        ],
        'lazy_blocked':[

        ],
        'backend_register':[
          'notBlank'
        ],
        'write_protect':[

        ],
        'url':[
          'notBlank'
        ],
        'authenticated':[

        ],
        'backend_status':[
          'notBlank'
        ],
        'id':[

        ],
        'no_sync':[

        ],
        'enacted':[

        ]
      },
      'id':8,
      'created':'2015-10-26T13:40:36.878Z',
      'updated':'2015-10-26T13:40:36.878Z',
      'enacted':null,
      'policed':null,
      'backend_register':'{}',
      'backend_status':'0 - Provisioning in progress',
      'deleted':false,
      'write_protect':false,
      'lazy_blocked':false,
      'no_sync':false,
      'origin_server_id':null,
      'url':'another.it',
      'contentProvider':'http://0.0.0.0:9000/hpcapi/contentproviders/1/',
      'authenticated':false,
      'enabled':true,
      'protocol':'http',
      'redirects':true,
      'description':null
    },
    {
      'humanReadableName':'test.it',
      'validators':{
        'updated':[

        ],
        'contentProvider':[
          'notBlank'
        ],
        'origin_server_id':[

        ],
        'policed':[

        ],
        'created':[

        ],
        'deleted':[

        ],
        'description':[

        ],
        'enabled':[

        ],
        'redirects':[

        ],
        'protocol':[
          'notBlank'
        ],
        'lazy_blocked':[

        ],
        'backend_register':[
          'notBlank'
        ],
        'write_protect':[

        ],
        'url':[
          'notBlank'
        ],
        'authenticated':[

        ],
        'backend_status':[
          'notBlank'
        ],
        'id':[

        ],
        'no_sync':[

        ],
        'enacted':[

        ]
      },
      'id':7,
      'created':'2015-10-26T13:36:42.567Z',
      'updated':'2015-10-26T13:36:42.567Z',
      'enacted':null,
      'policed':null,
      'backend_register':'{}',
      'backend_status':'0 - Provisioning in progress',
      'deleted':false,
      'write_protect':false,
      'lazy_blocked':false,
      'no_sync':false,
      'origin_server_id':null,
      'url':'test.it',
      'contentProvider':'http://0.0.0.0:9000/hpcapi/contentproviders/1/',
      'authenticated':false,
      'enabled':true,
      'protocol':'http',
      'redirects':true,
      'description':null
    },
    {
      'humanReadableName':'onlab.vicci.org',
      'validators':{
        'updated':[

        ],
        'contentProvider':[
          'notBlank'
        ],
        'origin_server_id':[

        ],
        'policed':[

        ],
        'created':[

        ],
        'deleted':[

        ],
        'description':[

        ],
        'enabled':[

        ],
        'redirects':[

        ],
        'protocol':[
          'notBlank'
        ],
        'lazy_blocked':[

        ],
        'backend_register':[
          'notBlank'
        ],
        'write_protect':[

        ],
        'url':[
          'notBlank'
        ],
        'authenticated':[

        ],
        'backend_status':[
          'notBlank'
        ],
        'id':[

        ],
        'no_sync':[

        ],
        'enacted':[

        ]
      },
      'id':2,
      'created':'2015-10-26T13:09:44.286Z',
      'updated':'2015-10-26T13:09:44.286Z',
      'enacted':null,
      'policed':null,
      'backend_register':'{}',
      'backend_status':'0 - Provisioning in progress',
      'deleted':false,
      'write_protect':false,
      'lazy_blocked':false,
      'no_sync':false,
      'origin_server_id':null,
      'url':'onlab.vicci.org',
      'contentProvider':'http://0.0.0.0:9000/hpcapi/contentproviders/1/',
      'authenticated':false,
      'enabled':true,
      'protocol':'HTTP',
      'redirects':true,
      'description':null
    },
    {
      'humanReadableName':'downloads.onosproject.org',
      'validators':{
        'updated':[

        ],
        'contentProvider':[
          'notBlank'
        ],
        'origin_server_id':[

        ],
        'policed':[

        ],
        'created':[

        ],
        'deleted':[

        ],
        'description':[

        ],
        'enabled':[

        ],
        'redirects':[

        ],
        'protocol':[
          'notBlank'
        ],
        'lazy_blocked':[

        ],
        'backend_register':[
          'notBlank'
        ],
        'write_protect':[

        ],
        'url':[
          'notBlank'
        ],
        'authenticated':[

        ],
        'backend_status':[
          'notBlank'
        ],
        'id':[

        ],
        'no_sync':[

        ],
        'enacted':[

        ]
      },
      'id':1,
      'created':'2015-10-26T13:09:44.182Z',
      'updated':'2015-10-26T13:09:44.182Z',
      'enacted':null,
      'policed':null,
      'backend_register':'{}',
      'backend_status':'0 - Provisioning in progress',
      'deleted':false,
      'write_protect':false,
      'lazy_blocked':false,
      'no_sync':false,
      'origin_server_id':null,
      'url':'downloads.onosproject.org',
      'contentProvider':'http://0.0.0.0:9000/hpcapi/contentproviders/1/',
      'authenticated':false,
      'enabled':true,
      'protocol':'HTTP',
      'redirects':true,
      'description':null
    }
  ],
  UserList: [
    {
      'humanReadableName':'teo@onlab.us',
      'validators':{
        'policed':[
          'notBlank'
        ],
        'site':[
          'notBlank'
        ],
        'is_appuser':[

        ],
        'is_staff':[

        ],
        'timezone':[
          'notBlank'
        ],
        'backend_status':[
          'notBlank'
        ],
        'id':[

        ],
        'is_registering':[

        ],
        'last_login':[
          'notBlank'
        ],
        'email':[
          'notBlank'
        ],
        'username':[
          'notBlank'
        ],
        'updated':[

        ],
        'login_page':[

        ],
        'firstname':[
          'notBlank'
        ],
        'user_url':[
          'url'
        ],
        'deleted':[

        ],
        'lastname':[
          'notBlank'
        ],
        'is_active':[

        ],
        'phone':[

        ],
        'is_admin':[

        ],
        'password':[
          'notBlank'
        ],
        'enacted':[
          'notBlank'
        ],
        'public_key':[

        ],
        'is_readonly':[

        ],
        'created':[

        ],
        'write_protect':[

        ]
      },
      'id':2,
      'password':'pbkdf2_sha256$12000$2Uzp1YCyjEBO$uU2irK//ZpEZYOIgLzanuApFoPnwfG1jNol2jD273wQ=',
      'last_login':'2015-10-26T14:11:27.625Z',
      'email':'teo@onlab.us',
      'username':'teo@onlab.us',
      'firstname':'Matteo',
      'lastname':'Scandolo',
      'phone':'',
      'user_url':null,
      'site':1,
      'public_key':'',
      'is_active':true,
      'is_admin':false,
      'is_staff':true,
      'is_readonly':false,
      'is_registering':false,
      'is_appuser':false,
      'login_page':null,
      'created':'2015-10-26T14:11:27.699Z',
      'updated':'2015-10-26T14:11:27.699Z',
      'enacted':null,
      'policed':null,
      'backend_status':'Provisioning in progress',
      'deleted':false,
      'write_protect':false,
      'timezone':'America/New_York'
    },
    {
      'humanReadableName':'padmin@vicci.org',
      'validators':{
        'policed':[
          'notBlank'
        ],
        'site':[
          'notBlank'
        ],
        'is_appuser':[

        ],
        'is_staff':[

        ],
        'timezone':[
          'notBlank'
        ],
        'backend_status':[
          'notBlank'
        ],
        'id':[

        ],
        'is_registering':[

        ],
        'last_login':[
          'notBlank'
        ],
        'email':[
          'notBlank'
        ],
        'username':[
          'notBlank'
        ],
        'updated':[

        ],
        'login_page':[

        ],
        'firstname':[
          'notBlank'
        ],
        'user_url':[
          'url'
        ],
        'deleted':[

        ],
        'lastname':[
          'notBlank'
        ],
        'is_active':[

        ],
        'phone':[

        ],
        'is_admin':[

        ],
        'password':[
          'notBlank'
        ],
        'enacted':[
          'notBlank'
        ],
        'public_key':[

        ],
        'is_readonly':[

        ],
        'created':[

        ],
        'write_protect':[

        ]
      },
      'id':1,
      'password':'pbkdf2_sha256$12000$Qufx9iqtaYma$xs0YurPOcj9qYQna/Qrb3K+im9Yr2XEVr0J4Kqek7AE=',
      'last_login':'2015-10-27T10:07:09.065Z',
      'email':'padmin@vicci.org',
      'username':'padmin@vicci.org',
      'firstname':'XOS',
      'lastname':'admin',
      'phone':null,
      'user_url':null,
      'site':1,
      'public_key':null,
      'is_active':true,
      'is_admin':true,
      'is_staff':true,
      'is_readonly':false,
      'is_registering':false,
      'is_appuser':false,
      'login_page':null,
      'created':'2015-02-17T22:06:38.059Z',
      'updated':'2015-10-27T09:00:44.672Z',
      'enacted':null,
      'policed':null,
      'backend_status':'Provisioning in progress',
      'deleted':false,
      'write_protect':false,
      'timezone':'America/New_York'
    }
  ]
};