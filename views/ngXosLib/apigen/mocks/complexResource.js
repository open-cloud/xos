module.exports = [ { element: 'category',
    meta: { classes: [ 'resourceGroup' ], title: 'Subscribers' },
    content:
     [ { element: 'copy',
         content: 'Resource related to the CORD Subscribers.\n\n' },
       { element: 'resource',
         meta: { title: 'Subscribers Collection' },
         attributes: { href: '/api/tenant/cord/subscriber/' },
         content:
          [ { element: 'transition',
              meta: { title: 'List All Subscribers' },
              content:
               [ { element: 'httpTransaction',
                   content:
                    [ { element: 'httpRequest',
                        attributes: { method: 'GET' },
                        content: [] },
                      { element: 'httpResponse',
                        attributes:
                         { statusCode: '200',
                           headers:
                            { element: 'httpHeaders',
                              content:
                               [ { element: 'member',
                                   content:
                                    { key: { element: 'string', content: 'Content-Type' },
                                      value: { element: 'string', content: 'application/json' } } } ] } },
                        content:
                         [ { element: 'asset',
                             meta: { classes: [ 'messageBody' ] },
                             attributes: { contentType: 'application/json' },
                             content: '[\n    {\n        "humanReadableName": "cordSubscriber-1",\n        "id": 1,\n        "features": {\n            "cdn": false,\n            "uplink_speed": 1000000000,\n            "downlink_speed": 1000000000,\n            "uverse": false,\n            "status": "enabled"\n        },\n        "identity": {\n            "account_num": "123",\n            "name": "My House"\n        },\n        "related": {\n            "instance_name": "mysite_vcpe",\n            "vsg_id": 4,\n            "compute_node_name": "node2.opencloud.us",\n            "c_tag": "432",\n            "instance_id": 1,\n            "wan_container_ip": null,\n            "volt_id": 3,\n            "s_tag": "222"\n        }\n    }\n]\n' } ] } ] } ] } ] },
       { element: 'resource',
         meta: { title: 'Subscribers Detail' },
         attributes: { href: '/api/tenant/cord/subscriber/{id}/' },
         content:
          [ { element: 'transition',
              meta: { title: 'View a Subscriber Detail' },
              attributes:
               { hrefVariables:
                  { element: 'hrefVariables',
                    content:
                     [ { element: 'member',
                         meta: { description: 'ID of the Subscriber in the form of an integer' },
                         content:
                          { key: { element: 'string', content: 'id' },
                            value: { element: 'number', content: 1 } } } ] } },
              content:
               [ { element: 'httpTransaction',
                   content:
                    [ { element: 'httpRequest',
                        attributes: { method: 'GET' },
                        content: [] },
                      { element: 'httpResponse',
                        attributes:
                         { statusCode: '200',
                           headers:
                            { element: 'httpHeaders',
                              content:
                               [ { element: 'member',
                                   content:
                                    { key: { element: 'string', content: 'Content-Type' },
                                      value: { element: 'string', content: 'application/json' } } } ] } },
                        content:
                         [ { element: 'asset',
                             meta: { classes: [ 'messageBody' ] },
                             attributes: { contentType: 'application/json' },
                             content: '{\n    "humanReadableName": "cordSubscriber-1", \n    "id": 1, \n    "features": { \n        "cdn": false, \n        "uplink_speed": 1000000000, \n        "downlink_speed": 1000000000, \n        "uverse": false, \n        "status": "enabled" \n    }, \n    "identity": { \n        "account_num": "123",\n        "name": "My House"\n    }, \n    "related": { \n        "instance_name": "mysite_vcpe", \n        "vsg_id": 4, \n        "compute_node_name": "node2.opencloud.us",\n        "c_tag": "432", \n        "instance_id": 1, \n        "wan_container_ip": null, \n        "volt_id": 3, \n        "s_tag": "222" \n    } \n}\n' } ] } ] } ] },
            { element: 'transition',
              meta: { title: 'Delete a Subscriber' },
              attributes:
               { hrefVariables:
                  { element: 'hrefVariables',
                    content:
                     [ { element: 'member',
                         meta: { description: 'ID of the Subscriber in the form of an integer' },
                         content:
                          { key: { element: 'string', content: 'id' },
                            value: { element: 'number', content: 1 } } } ] } },
              content:
               [ { element: 'httpTransaction',
                   content:
                    [ { element: 'httpRequest',
                        attributes: { method: 'DELETE' },
                        content: [] },
                      { element: 'httpResponse',
                        attributes: { statusCode: '204' },
                        content: [] } ] } ] } ] },
       { element: 'resource',
         meta: { title: 'Subscriber features' },
         attributes:
          { href: '/api/tenant/cord/subscriber/{id}/features/',
            hrefVariables:
             { element: 'hrefVariables',
               content:
                [ { element: 'member',
                    meta: { description: 'ID of the Subscriber in the form of an integer' },
                    content:
                     { key: { element: 'string', content: 'id' },
                       value: { element: 'number', content: 1 } } } ] } },
         content:
          [ { element: 'transition',
              meta: { title: 'View a Subscriber Features Detail' },
              content:
               [ { element: 'httpTransaction',
                   content:
                    [ { element: 'httpRequest',
                        attributes: { method: 'GET' },
                        content: [] },
                      { element: 'httpResponse',
                        attributes:
                         { statusCode: '200',
                           headers:
                            { element: 'httpHeaders',
                              content:
                               [ { element: 'member',
                                   content:
                                    { key: { element: 'string', content: 'Content-Type' },
                                      value: { element: 'string', content: 'application/json' } } } ] } },
                        content:
                         [ { element: 'asset',
                             meta: { classes: [ 'messageBody' ] },
                             attributes: { contentType: 'application/json' },
                             content: '{\n    "cdn": false, \n    "uplink_speed": 1000000000, \n    "downlink_speed": 1000000000, \n    "uverse": true, \n    "status": "enabled"\n}\n' } ] } ] } ] } ] },
       { element: 'resource',
         meta: { title: 'Subscriber features uplink_speed' },
         attributes:
          { href: '/api/tenant/cord/subscriber/{id}/features/uplink_speed/',
            hrefVariables:
             { element: 'hrefVariables',
               content:
                [ { element: 'member',
                    meta: { description: 'ID of the Subscriber in the form of an integer' },
                    content:
                     { key: { element: 'string', content: 'id' },
                       value: { element: 'number', content: 1 } } } ] } },
         content:
          [ { element: 'transition',
              meta: { title: 'Read Subscriber uplink_speed' },
              content:
               [ { element: 'httpTransaction',
                   content:
                    [ { element: 'httpRequest',
                        attributes: { method: 'GET' },
                        content: [] },
                      { element: 'httpResponse',
                        attributes:
                         { statusCode: '200',
                           headers:
                            { element: 'httpHeaders',
                              content:
                               [ { element: 'member',
                                   content:
                                    { key: { element: 'string', content: 'Content-Type' },
                                      value: { element: 'string', content: 'application/json' } } } ] } },
                        content:
                         [ { element: 'asset',
                             meta: { classes: [ 'messageBody' ] },
                             attributes: { contentType: 'application/json' },
                             content: '{\n    "uplink_speed": 1000000000\n}\n' } ] } ] } ] },
            { element: 'transition',
              meta: { title: 'Update Subscriber uplink_speed' },
              content:
               [ { element: 'httpTransaction',
                   content:
                    [ { element: 'httpRequest',
                        meta: { title: '200' },
                        attributes:
                         { method: 'PUT',
                           headers:
                            { element: 'httpHeaders',
                              content:
                               [ { element: 'member',
                                   content:
                                    { key: { element: 'string', content: 'Content-Type' },
                                      value: { element: 'string', content: 'application/json' } } } ] } },
                        content:
                         [ { element: 'asset',
                             meta: { classes: [ 'messageBody' ] },
                             attributes: { contentType: 'application/json' },
                             content: '{\n    "uplink_speed": 1000000000\n}\n' } ] },
                      { element: 'httpResponse',
                        attributes:
                         { statusCode: '200',
                           headers:
                            { element: 'httpHeaders',
                              content:
                               [ { element: 'member',
                                   content:
                                    { key: { element: 'string', content: 'Content-Type' },
                                      value: { element: 'string', content: 'application/json' } } } ] } },
                        content:
                         [ { element: 'asset',
                             meta: { classes: [ 'messageBody' ] },
                             attributes: { contentType: 'application/json' },
                             content: '{\n    "uplink_speed": 1000000000\n}\n' } ] } ] } ] } ] },
       { element: 'resource',
         meta: { title: 'Subscriber features downlink_speed' },
         attributes:
          { href: '/api/tenant/cord/subscriber/{id}/features/downlink_speed/',
            hrefVariables:
             { element: 'hrefVariables',
               content:
                [ { element: 'member',
                    meta: { description: 'ID of the Subscriber in the form of an integer' },
                    content:
                     { key: { element: 'string', content: 'id' },
                       value: { element: 'number', content: 1 } } } ] } },
         content:
          [ { element: 'transition',
              meta: { title: 'Read Subscriber downlink_speed' },
              content:
               [ { element: 'httpTransaction',
                   content:
                    [ { element: 'httpRequest',
                        attributes: { method: 'GET' },
                        content: [] },
                      { element: 'httpResponse',
                        attributes:
                         { statusCode: '200',
                           headers:
                            { element: 'httpHeaders',
                              content:
                               [ { element: 'member',
                                   content:
                                    { key: { element: 'string', content: 'Content-Type' },
                                      value: { element: 'string', content: 'application/json' } } } ] } },
                        content:
                         [ { element: 'asset',
                             meta: { classes: [ 'messageBody' ] },
                             attributes: { contentType: 'application/json' },
                             content: '{\n    "downlink_speed": 1000000000\n}\n' } ] } ] } ] },
            { element: 'transition',
              meta: { title: 'Update Subscriber downlink_speed' },
              content:
               [ { element: 'httpTransaction',
                   content:
                    [ { element: 'httpRequest',
                        meta: { title: '200' },
                        attributes:
                         { method: 'PUT',
                           headers:
                            { element: 'httpHeaders',
                              content:
                               [ { element: 'member',
                                   content:
                                    { key: { element: 'string', content: 'Content-Type' },
                                      value: { element: 'string', content: 'application/json' } } } ] } },
                        content:
                         [ { element: 'asset',
                             meta: { classes: [ 'messageBody' ] },
                             attributes: { contentType: 'application/json' },
                             content: '{\n    "downlink_speed": 1000000000\n}\n' } ] },
                      { element: 'httpResponse',
                        attributes:
                         { statusCode: '200',
                           headers:
                            { element: 'httpHeaders',
                              content:
                               [ { element: 'member',
                                   content:
                                    { key: { element: 'string', content: 'Content-Type' },
                                      value: { element: 'string', content: 'application/json' } } } ] } },
                        content:
                         [ { element: 'asset',
                             meta: { classes: [ 'messageBody' ] },
                             attributes: { contentType: 'application/json' },
                             content: '{\n    "downlink_speed": 1000000000\n}\n' } ] } ] } ] } ] },
       { element: 'resource',
         meta: { title: 'Subscriber features cdn' },
         attributes:
          { href: '/api/tenant/cord/subscriber/{id}/features/cdn/',
            hrefVariables:
             { element: 'hrefVariables',
               content:
                [ { element: 'member',
                    meta: { description: 'ID of the Subscriber in the form of an integer' },
                    content:
                     { key: { element: 'string', content: 'id' },
                       value: { element: 'number', content: 1 } } } ] } },
         content:
          [ { element: 'transition',
              meta: { title: 'Read Subscriber cdn' },
              content:
               [ { element: 'httpTransaction',
                   content:
                    [ { element: 'httpRequest',
                        attributes: { method: 'GET' },
                        content: [] },
                      { element: 'httpResponse',
                        attributes:
                         { statusCode: '200',
                           headers:
                            { element: 'httpHeaders',
                              content:
                               [ { element: 'member',
                                   content:
                                    { key: { element: 'string', content: 'Content-Type' },
                                      value: { element: 'string', content: 'application/json' } } } ] } },
                        content:
                         [ { element: 'asset',
                             meta: { classes: [ 'messageBody' ] },
                             attributes: { contentType: 'application/json' },
                             content: '{\n    "cdn": false\n}\n' } ] } ] } ] },
            { element: 'transition',
              meta: { title: 'Update Subscriber cdn' },
              content:
               [ { element: 'httpTransaction',
                   content:
                    [ { element: 'httpRequest',
                        meta: { title: '200' },
                        attributes:
                         { method: 'PUT',
                           headers:
                            { element: 'httpHeaders',
                              content:
                               [ { element: 'member',
                                   content:
                                    { key: { element: 'string', content: 'Content-Type' },
                                      value: { element: 'string', content: 'application/json' } } } ] } },
                        content:
                         [ { element: 'asset',
                             meta: { classes: [ 'messageBody' ] },
                             attributes: { contentType: 'application/json' },
                             content: '{\n    "cdn": false\n}\n' } ] },
                      { element: 'httpResponse',
                        attributes:
                         { statusCode: '200',
                           headers:
                            { element: 'httpHeaders',
                              content:
                               [ { element: 'member',
                                   content:
                                    { key: { element: 'string', content: 'Content-Type' },
                                      value: { element: 'string', content: 'application/json' } } } ] } },
                        content:
                         [ { element: 'asset',
                             meta: { classes: [ 'messageBody' ] },
                             attributes: { contentType: 'application/json' },
                             content: '{\n    "cdn": false\n}\n' } ] } ] } ] } ] },
       { element: 'resource',
         meta: { title: 'Subscriber features uverse' },
         attributes:
          { href: '/api/tenant/cord/subscriber/{id}/features/uverse/',
            hrefVariables:
             { element: 'hrefVariables',
               content:
                [ { element: 'member',
                    meta: { description: 'ID of the Subscriber in the form of an integer' },
                    content:
                     { key: { element: 'string', content: 'id' },
                       value: { element: 'number', content: 1 } } } ] } },
         content:
          [ { element: 'transition',
              meta: { title: 'Read Subscriber uverse' },
              content:
               [ { element: 'httpTransaction',
                   content:
                    [ { element: 'httpRequest',
                        attributes: { method: 'GET' },
                        content: [] },
                      { element: 'httpResponse',
                        attributes:
                         { statusCode: '200',
                           headers:
                            { element: 'httpHeaders',
                              content:
                               [ { element: 'member',
                                   content:
                                    { key: { element: 'string', content: 'Content-Type' },
                                      value: { element: 'string', content: 'application/json' } } } ] } },
                        content:
                         [ { element: 'asset',
                             meta: { classes: [ 'messageBody' ] },
                             attributes: { contentType: 'application/json' },
                             content: '{\n    "uverse": false\n}\n' } ] } ] } ] },
            { element: 'transition',
              meta: { title: 'Update Subscriber uverse' },
              content:
               [ { element: 'httpTransaction',
                   content:
                    [ { element: 'httpRequest',
                        meta: { title: '200' },
                        attributes:
                         { method: 'PUT',
                           headers:
                            { element: 'httpHeaders',
                              content:
                               [ { element: 'member',
                                   content:
                                    { key: { element: 'string', content: 'Content-Type' },
                                      value: { element: 'string', content: 'application/json' } } } ] } },
                        content:
                         [ { element: 'asset',
                             meta: { classes: [ 'messageBody' ] },
                             attributes: { contentType: 'application/json' },
                             content: '{\n    "uverse": false\n}\n' } ] },
                      { element: 'httpResponse',
                        attributes:
                         { statusCode: '200',
                           headers:
                            { element: 'httpHeaders',
                              content:
                               [ { element: 'member',
                                   content:
                                    { key: { element: 'string', content: 'Content-Type' },
                                      value: { element: 'string', content: 'application/json' } } } ] } },
                        content:
                         [ { element: 'asset',
                             meta: { classes: [ 'messageBody' ] },
                             attributes: { contentType: 'application/json' },
                             content: '{\n    "uverse": false\n}\n' } ] } ] } ] } ] },
       { element: 'resource',
         meta: { title: 'Subscriber features status' },
         attributes:
          { href: '/api/tenant/cord/subscriber/{id}/features/status/',
            hrefVariables:
             { element: 'hrefVariables',
               content:
                [ { element: 'member',
                    meta: { description: 'ID of the Subscriber in the form of an integer' },
                    content:
                     { key: { element: 'string', content: 'id' },
                       value: { element: 'number', content: 1 } } } ] } },
         content:
          [ { element: 'transition',
              meta: { title: 'Read Subscriber status' },
              content:
               [ { element: 'httpTransaction',
                   content:
                    [ { element: 'httpRequest',
                        attributes: { method: 'GET' },
                        content: [] },
                      { element: 'httpResponse',
                        attributes:
                         { statusCode: '200',
                           headers:
                            { element: 'httpHeaders',
                              content:
                               [ { element: 'member',
                                   content:
                                    { key: { element: 'string', content: 'Content-Type' },
                                      value: { element: 'string', content: 'application/json' } } } ] } },
                        content:
                         [ { element: 'asset',
                             meta: { classes: [ 'messageBody' ] },
                             attributes: { contentType: 'application/json' },
                             content: '{\n    "status": "enabled"\n}\n' } ] } ] } ] },
            { element: 'transition',
              meta: { title: 'Update Subscriber status' },
              content:
               [ { element: 'httpTransaction',
                   content:
                    [ { element: 'httpRequest',
                        meta: { title: '200' },
                        attributes:
                         { method: 'PUT',
                           headers:
                            { element: 'httpHeaders',
                              content:
                               [ { element: 'member',
                                   content:
                                    { key: { element: 'string', content: 'Content-Type' },
                                      value: { element: 'string', content: 'application/json' } } } ] } },
                        content:
                         [ { element: 'asset',
                             meta: { classes: [ 'messageBody' ] },
                             attributes: { contentType: 'application/json' },
                             content: '{\n    "status": "enabled"\n}\n' } ] },
                      { element: 'httpResponse',
                        attributes:
                         { statusCode: '200',
                           headers:
                            { element: 'httpHeaders',
                              content:
                               [ { element: 'member',
                                   content:
                                    { key: { element: 'string', content: 'Content-Type' },
                                      value: { element: 'string', content: 'application/json' } } } ] } },
                        content:
                         [ { element: 'asset',
                             meta: { classes: [ 'messageBody' ] },
                             attributes: { contentType: 'application/json' },
                             content: '{\n    "status": "enabled"\n}\n' } ] } ] } ] } ] } ] } ]