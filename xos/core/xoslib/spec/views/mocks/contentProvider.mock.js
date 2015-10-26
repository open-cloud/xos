/* eslint-disable key-spacing */

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
      'contentProvider':'http://0.0.0.0:9000/hpcapi/contentproviders/1/',
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
      'contentProvider':'http://0.0.0.0:9000/hpcapi/contentproviders/2/',
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
  ]
};