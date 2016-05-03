module.exports = [
  {
    element: 'category',
    meta: {
      classes: ['resourceGroup'],
      title: 'Instances'
    },
    content: [
      {
        element: 'copy',
        content: 'List of the XOS instances\n\n'
      },
      {
        element: 'resource',
        meta: {
          title: 'Instances Collection'
        },
        attributes: {
          href: '/api/core/instances/{?no_hyperlinks}'
        },
        content: [
          {
            element: 'copy',
            content: '    + no_hyperlinks (number, optional) - Wheter to return relation with links or ids\n        + Default: `0`\n\n'
          },
          {
            element: 'transition',
            meta: {
              title: 'List all Instances'
            },
            content: [
              {
                element: 'httpTransaction',
                content: [
                  {
                    element: 'httpRequest',
                    attributes: {
                      method: 'GET'
                    },
                    content: []
                  },
                  {
                    element: 'httpResponse',
                    attributes: {
                      statusCode: '200',
                      headers:
                        {
                          element: 'httpHeaders',
                          content: [
                            {
                              element: 'member',
                              content: {
                                key: {
                                  element: 'string',
                                  content: 'Content-Type'
                                },
                                value: {
                                  element: 'string',
                                  content: 'application/json'
                                }
                              }
                            }
                          ]
                        }
                    },
                    content: [
                      {
                        element: 'asset',
                        meta: {
                          classes: ['messageBody']
                        },
                        attributes: {
                          contentType: 'application/json'
                        },
                        content: '[\n    {\n        "id": 1,\n        "humanReadableName": "uninstantiated-1",\n        "created": "2016-04-26T00:36:22.465259Z",\n        "updated": "2016-04-26T00:36:22.465288Z",\n        "enacted": null,\n        "policed": null,\n        "backend_register": "{}",\n        "backend_status": "0 - Provisioning in progress",\n        "deleted": false,\n        "write_protect": false,\n        "lazy_blocked": false,\n        "no_sync": false,\n        "instance_id": null,\n        "instance_uuid": null,\n        "name": "mysite_vcpe",\n        "instance_name": null,\n        "ip": null,\n        "image": "1",\n        "creator": "1",\n        "slice": "1",\n        "deployment": "1",\n        "node": "1",\n        "numberCores": 0,\n        "flavor": "1",\n        "userData": null,\n        "isolation": "vm",\n        "volumes": "/etc/dnsmasq.d,/etc/ufw",\n        "parent": null,\n        "networks": [\n            "1"\n        ]\n    }\n]\n'
                      }
                    ]
                  }
                ]
              }
            ]
          },
          {
            element: 'transition',
            meta: {
              title: 'Create an Instance'
            },
            attributes: {
              hrefVariables: {
                element: 'hrefVariables',
                content: [
                  {
                    element: 'member',
                    content: {
                      key: {
                        element: 'string',
                        content: 'no_hyperlinks'
                      },
                      value: {
                        element: 'string',
                        content: '1'
                      }
                    }
                  }
                ]
              }
            },
            content: [
              {
                element: 'httpTransaction',
                content: [
                  {
                    element: 'httpRequest',
                    attributes: {
                      method: 'POST',
                      headers: {
                        element: 'httpHeaders',
                        content: [
                          {
                            element: 'member',
                            content: {
                              key: {
                                element: 'string',
                                content: 'Content-Type'
                              },
                              value: {
                                element: 'string',
                                content: 'application/json'
                              }
                            }
                          }
                        ]
                      }
                    },
                    content: [
                      {
                        element: 'asset',
                        meta: {
                          classes: ['messageBody']
                        },
                        attributes: {
                          contentType: 'application/json'
                        },
                        content: '{\n    "name": "test-instance",\n    "image": 1,\n    "slice": 1,\n    "deployment": 1,\n    "node": 1\n}\n'
                      }
                    ]
                  },
                  {
                    element: 'httpResponse',
                    attributes: {
                      statusCode: '200',
                      headers: {
                        element: 'httpHeaders',
                        content: [
                          {
                            element: 'member',
                            content: {
                              key: {
                                element: 'string',
                                content: 'Content-Type'
                              },
                              value: {
                                element: 'string',
                                content: 'application/json'
                              }
                            }
                          }
                        ]
                      }
                    },
                    content: [
                      {
                        element: 'asset',
                        meta: {
                          classes: ['messageBody']
                        },
                        attributes: {
                          contentType: 'application/json'
                        },
                        content: '{\n    "id": 1,\n    "humanReadableName": "uninstantiated-1",\n    "created": "2016-04-26T00:36:22.465259Z",\n    "updated": "2016-04-26T00:36:22.465288Z",\n    "enacted": null,\n    "policed": null,\n    "backend_register": "{}",\n    "backend_status": "0 - Provisioning in progress",\n    "deleted": false,\n    "write_protect": false,\n    "lazy_blocked": false,\n    "no_sync": false,\n    "instance_id": null,\n    "instance_uuid": null,\n    "name": "test-instance",\n    "instance_name": null,\n    "ip": null,\n    "image": "1",\n    "creator": "1",\n    "slice": "1",\n    "deployment": "1",\n    "node": "1",\n    "numberCores": 0,\n    "flavor": "1",\n    "userData": null,\n    "isolation": "vm",\n    "volumes": "/etc/dnsmasq.d,/etc/ufw",\n    "parent": null,\n    "networks": [\n        "1"\n    ]\n}\n'
                      }
                    ]
                  }
                ]
              }
            ]
          }
        ]
      },
      {
        element: 'resource',
        meta: {
          title: 'Instances Detail'
        },
        attributes: {
          href: '/api/core/instances/{id}/'
        },
        content: [
          {
            element: 'transition',
            meta: {
              title: 'Get instance details'
            },
            attributes: {
              hrefVariables: {
                element: 'hrefVariables',
                content: [
                  {
                    element: 'member',
                    meta: {
                      description: 'ID of the Instance in the form of an integer'
                    },
                    content: {
                      key: {
                        element: 'string',
                        content: 'id'
                      },
                      value: {
                        element: 'number',
                        content: 1
                      }
                    }
                  }
                ]
              }
            },
            content: [
              {
                element: 'httpTransaction',
                content: [
                  {
                    element: 'httpRequest',
                    attributes: {
                      method: 'GET'
                    },
                    content: []
                  },
                  {
                    element: 'httpResponse',
                    attributes: {
                      statusCode: '200',
                      headers: {
                        element: 'httpHeaders',
                        content: [
                          {
                            element: 'member',
                            content: {
                              key: {
                                element: 'string',
                                content: 'Content-Type'
                              },
                              value: {
                                element: 'string',
                                content: 'application/json'
                              }
                            }
                          }
                        ]
                      }
                    },
                    content: [
                      {
                        element: 'asset',
                        meta: {
                          classes: ['messageBody']
                        },
                        attributes: {
                          contentType: 'application/json'
                        },
                        content: '{\n    "id": 1,\n    "humanReadableName": "uninstantiated-1",\n    "created": "2016-04-26T00:36:22.465259Z",\n    "updated": "2016-04-26T00:36:22.465288Z",\n    "enacted": null,\n    "policed": null,\n    "backend_register": "{}",\n    "backend_status": "0 - Provisioning in progress",\n    "deleted": false,\n    "write_protect": false,\n    "lazy_blocked": false,\n    "no_sync": false,\n    "instance_id": null,\n    "instance_uuid": null,\n    "name": "mysite_vcpe",\n    "instance_name": null,\n    "ip": null,\n    "image": "1",\n    "creator": "1",\n    "slice": "1",\n    "deployment": "1",\n    "node": "1",\n    "numberCores": 0,\n    "flavor": "1",\n    "userData": null,\n    "isolation": "vm",\n    "volumes": "/etc/dnsmasq.d,/etc/ufw",\n    "parent": null,\n    "networks": [\n        "1"\n    ]\n}\n'
                      }
                    ]
                  }
                ]
              }
            ]
          },
          {
            element: 'transition',
            meta: {
              title: 'Delete instance'
            },
            attributes: {
              hrefVariables: {
                element: 'hrefVariables',
                content: [
                  {
                    element: 'member',
                    meta: {
                      description: 'ID of the Instance in the form of an integer'
                    },
                    content: {
                      key: {
                        element: 'string',
                        content: 'id'
                      },
                      value: {
                        element: 'number',
                        content: 1
                      }
                    }
                  }
                ]
              }
            },
            content: [
              {
                element: 'httpTransaction',
                content: [
                  {
                    element: 'httpRequest',
                    attributes: {
                      method: 'DELETE'
                    },
                    content: []
                  },
                  {
                    element: 'httpResponse',
                    attributes: {
                      statusCode: '204'
                    },
                    content: []
                  }
                ]
              }
            ]
          }
        ]
      }
    ]
  }
];