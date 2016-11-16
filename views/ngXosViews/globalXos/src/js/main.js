'use strict';

angular.module('xos.globalXos', [
  'ngResource',
  'ngCookies',
  'ui.router',
  'xos.helpers',
  'ui.bootstrap.modal',
  'ui.bootstrap.tpls'
])
.config(($stateProvider) => {
  $stateProvider
  .state('xos-list', {
    url: '/',
    template: '<xos-list></xos-list>'
  });
})
.config(function($httpProvider){
  $httpProvider.interceptors.push('NoHyperlinks');
})
.value('LXOS', [])
.directive('xosList', function(){
  return {
    restrict: 'E',
    scope: {},
    bindToController: true,
    controllerAs: 'vm',
    templateUrl: 'templates/xos-list.tpl.html',
    controller: function($window, $q, _, Controllers, LXOS, LocalAuth, LocalSlices, LocalUsers, $uibModal, Slices){
      const self = this;
      $q.all([
        Controllers.query({backend_type: 'CORD'}).$promise,
        Slices.query().$promise
      ])
      .then(res => {
        [this.xoss, this.gSlices] = res;
      });

      this.openLocally = (itemKind) => {
        return (item) => {
          $window.open(`${item.xos.auth_url}admin/core/${itemKind}/${item.id}`, '_blank');
        }
      };

      const getGlobalInstances = (item) => {
        $uibModal.open({
          animation: true,
          size: 'lg',
          templateUrl: 'listInstances.html',
          controllerAs: 'vm',
          resolve: {
            slice: function () {
              return {
                name: item.name,
                xos: {
                  name: 'G-XOS'
                }
              };
            }
          },
          controller: function($uibModalInstance, slice, LocalInstances, LocalSlices) {
            this.slice = slice;

            this.config = {
              columns: [
                {
                  label: 'Name',
                  prop: 'name',
                }
              ],
              actions: [
                {
                  label: 'Add Instance',
                  icon: 'remove',
                  color: 'red',
                  cb: (item) => {
                    console.log(item);
                    LocalInstances.deleteFromLocal(item)
                    .then(() => {
                      _.remove(this.instances, i => i.id === item.id);
                    });
                  }
                }
              ]
            };

            LocalSlices.queryFromAll(self.xoss).$promise
            .then(slices => {
              // keep only the slice that match the name
              this.slicesId = slices
                .filter(s => s.name.indexOf(this.slice.name) > -1)
                .reduce((o, s) => {
                  o[s.xos.id] = s.id;
                  return o;
                }, {});
              return LocalInstances.queryFromAll(self.xoss).$promise;
            })
            .then(instances => {
              this.instances = instances.filter(i => this.slicesId[i.xos.id] === i.slice);
            })
            .catch(e => {
              this.instances = [];
            });

            this.close = () => {
              $uibModalInstance.dismiss('cancel');
            }
          }
        })
      };

      const createGlobalInstance = (item) => {
        $uibModal.open({
          animation: true,
          size: 'lg',
          templateUrl: 'addInstance.html',
          controller: function($scope, $q, $uibModalInstance, slice, LocalInstances, LocalAuth){
            this.slice = slice;

            this.model = {
              // isolation: 'vm'
            };

            let xos;

            Controllers.query({backend_type: 'CORD'}).$promise
            .then((xos) => {
              this.xoss = xos;
              this.config.fields['xos'].options = _.map(xos, item => {
                return {id: item.id, label: item.name}
              });
            });

            $scope.$watch(() => this.model.xos, () => {
              if(!this.model.xos){
                return;
              }
              xos = _.find(this.xoss, {id: this.model.xos});
              LocalInstances.getLocalInfo(xos)
              .then((res) => {
                [
                  this.config.fields['deployment'].options,
                  this.config.fields['image'].options,
                  this.config.fields['flavor'].options,
                  this.config.fields['node'].options
                ] = res;
                return $q.all([
                  LocalSlices.getLocalByName(xos, this.slice.name),
                  LocalAuth.getUserByName(xos, xos.admin_user)
                ]);
              })
              .then((res) => {
                console.log('aaaa: ', res);
                [this.localSlice, this.user] = res;
              });
            });


            this.config = {
              formName: 'instanceForm',
              order: ['xos', 'name'],
              excludedFields: ['xos', 'slice'],
              actions: [
                {
                  label: 'Save',
                  icon: 'ok',
                  cb: (instance) => {
                    instance.xos = xos;
                    instance.slice = this.localSlice.id;
                    instance.creator = this.user.id;
                    LocalInstances.createOnLocal(instance)
                    .then(res => {
                      slice.instance_total = slice.instance_total + 1;
                      $uibModalInstance.close();
                    });
                  },
                  class: 'success'
                },
                {
                  label: 'Cancel',
                  icon: 'remove',
                  cb: () => {
                    $uibModalInstance.dismiss('cancel');
                  },
                  class: 'warning'
                }
              ],
              fields: {
                xos: {
                  type: 'select',
                  validators: {
                    required: true
                  }
                },
                name: {
                  type: 'text',
                  validators: {
                    required: true
                  }
                },
                deployment: {
                  type: 'select',
                  validators: {
                    required: true
                  }
                },
                node: {
                  type: 'select',
                  validators: {
                    required: true
                  }
                },
                image: {
                  type: 'select',
                  validators: {
                    required: true,
                  }
                },
                flavor: {
                  type: 'select',
                  validators: {
                    required: true,
                  }
                },
                isolation: {
                  type: 'select',
                  options: [
                    {id: 'vm', label: 'VM'},
                    {id: 'container', label: 'Container'},
                    {id: 'container_vm', label: 'Container in VM'}
                  ],
                  validators: {
                    required: true,
                  }
                },
              }
            };
          },
          controllerAs: 'vm',
          resolve: {
            slice: function () {
              return item;
            }
          }
        });
      };

      const baseSliceCols = [
        {
          label: 'Name',
          prop: 'name',
        },
        // {
        //   label: 'Mount Data Sets',
        //   prop: 'mount_data_sets'
        // }
      ];

      const lXosSliceCols = [
        {
          label: 'Max Instances',
          prop: 'max_instances'
        },
        {
          label: 'Instances',
          prop: 'instance_total'
        },
        {
          label: 'L-XOS',
          type: 'custom',
          formatter: item => item.xos.name
        }
      ];

      this.gSliceTableCgf = {
        columns: baseSliceCols,
        filter: 'field',
        order: true,
        actions: [
          {
            label: 'Get Instances',
            icon: 'search',
            cb: getGlobalInstances
          },
          {
            label: 'Add Instances',
            icon: 'plus',
            cb: createGlobalInstance
          },
        ]
      };

      this.sliceTableCfg = {
        columns: baseSliceCols.concat(lXosSliceCols),
        actions: [
          {
            label: 'open locally',
            icon: 'open',
            cb: this.openLocally('slice')
          },
          {
            label: 'Get Instances',
            icon: 'search',
            cb: (item) => {
              $uibModal.open({
                animation: true,
                size: 'lg',
                templateUrl: 'listInstances.html',
                controllerAs: 'vm',
                resolve: {
                  slice: function () {
                    return item;
                  }
                },
                controller: function($uibModalInstance, slice, LocalInstances) {
                  this.slice = slice;

                  this.config = {
                    columns: [
                      {
                        label: 'Name',
                        prop: 'name',
                      },
                      {
                        label: 'deployment',
                        prop: 'deployment',
                      },
                    ]
                  };

                  LocalInstances.getFromLocal(slice.xos)
                  .then(instances => {
                    this.instances = instances.filter(i => i.slice === slice.id);
                  });

                  this.close = () => {
                    $uibModalInstance.dismiss('cancel');
                  }
                }
              })
            }
          },
          {
            label: 'Add Instance',
            icon: 'plus',
            cb: (item) => {
              $uibModal.open({
                animation: true,
                size: 'lg',
                templateUrl: 'addInstance.html',
                controller: function($uibModalInstance, slice, LocalInstances){
                  this.slice = slice;

                  this.model = {};
                  console.log(slice);
                  LocalInstances.getLocalInfo(slice.xos)
                  .then((res) => {
                    [
                      this.config.fields['deployment'].options,
                      this.config.fields['image'].options,
                      this.config.fields['flavor'].options,
                      this.config.fields['node'].options
                    ] = res;
                  });

                  this.config = {
                    formName: 'instanceForm',
                    excludedFields: ['xos', 'slice'],
                    actions: [
                      {
                        label: 'Save',
                        icon: 'ok',
                        cb: (instance) => {
                          instance.xos = slice.xos;
                          instance.slice = slice.id;
                          instance.creator = this.user.id;
                          LocalInstances.createOnLocal(instance)
                          .then(res => {
                            slice.instance_total = slice.instance_total + 1;
                            $uibModalInstance.close();
                          });
                        },
                        class: 'success'
                      },
                      {
                        label: 'Cancel',
                        icon: 'remove',
                        cb: () => {
                          $uibModalInstance.dismiss('cancel');
                        },
                        class: 'warning'
                      }
                    ],
                    fields: {
                      name: {
                        type: 'text',
                        validators: {
                          required: true
                        }
                      },
                      deployment: {
                        type: 'select',
                        validators: {
                          required: true
                        }
                      },
                      node: {
                        type: 'select',
                        validators: {
                          required: true
                        }
                      },
                      image: {
                        type: 'select',
                        validators: {
                          required: true,
                        }
                      },
                      flavor: {
                        type: 'select',
                        validators: {
                          required: true,
                        }
                      },
                      isolation: {
                        type: 'select',
                        options: [
                          {id: 'vm', label: 'VM'},
                          {id: 'container', label: 'Container'},
                          {id: 'container_vm', label: 'Container in VM'}
                        ],
                        validators: {
                          required: true,
                        }
                      },
                    }
                  };
                },
                controllerAs: 'vm',
                resolve: {
                  slice: function () {
                    return item;
                  }
                }
              });
            }
          }
        ],
        filter: 'field',
        order: true
      };

      this.usersTableCfg = {
        columns: [
          {
            label: 'Name',
            type: 'custom',
            formatter: item => `${item.firstname} ${item.lastname}`
          },
          {
            label: 'E-Mail',
            prop: 'email'
          },
          {
            label: 'User Name',
            prop: 'username'
          },
          {
            label: 'Time Zone',
            prop: 'timezone'
          },
          {
            label: 'L-XOS',
            type: 'custom',
            formatter: item => item.xos.name
          }
        ],
        actions: [
          {
            label: 'open locally',
            icon: 'open',
            cb: this.openLocally('user')
          }
        ],
        filter: 'field',
        order: true
      };

      this.toggleXos = (xos) => {
        if(_.findIndex(LXOS, {id: xos.id}) > -1){
          xos.active = false;
          _.remove(LXOS, {id: xos.id});
        }
        else{
          xos.active = true;
          LXOS.push(xos);
        }

        // authenticate on L-XOS
        LocalAuth.login()
        .then(() => {
          // fetch slices
          return $q.all([
            LocalSlices.queryFromAll().$promise,
            LocalUsers.queryFromAll().$promise,
          ]);
        })
        .then(res => {
          [this.localSlices, this.localUsers] = res;
        })
        .catch(e => {
          console.log(e);
        });
      }
    }
  };
});