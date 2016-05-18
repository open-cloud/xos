'use strict';

angular.module('xos.contentProvider', [
  'ngResource',
  'ngCookies',
  'xos.helpers',
  'ui.router'
])
.config(($stateProvider) => {

  $stateProvider
  .state('list', {
    url: '/',
    template: '<content-provider-list></content-provider-list>',
  })
  .state('details', {
    url: '/contentProvider/:id',
    template: '<content-provider-detail></content-provider-detail>'
  })
  .state('cdn', {
    url: '/contentProvider/:id/cdn_prefix',
    template: '<content-provider-cdn></content-provider-cdn>'
  })
  .state('server', {
    url: '/contentProvider/:id/origin_server',
    template: '<content-provider-server></content-provider-server>'
  })
  .state('users', {
    url: '/contentProvider/:id/users',
    template: '<content-provider-users></content-provider-users>'
  });
})
.config(function($httpProvider){
  // add X-CSRFToken header for update, create, delete (!GET)
  $httpProvider.interceptors.push('SetCSRFToken');
  $httpProvider.interceptors.push('NoHyperlinks');
})
.service('ContentProvider', function($resource){
  return $resource('/hpcapi/contentproviders/:id/', {id: '@id'}, {
    'update': {method: 'PUT'}
  });
})
.service('ServiceProvider', function($resource){
  return $resource('/hpcapi/serviceproviders/:id/', {id: '@id'});
})
.service('CdnPrefix', function($resource){
  return $resource('/hpcapi/cdnprefixs/:id/', {id: '@id'});
})
.service('OriginServer', function($resource){
  return $resource('/hpcapi/originservers/:id/', {id: '@id'});
})
.service('User', function($resource){
  return $resource('/xos/users/:id/', {id: '@id'});
})
.directive('cpActions', function(ContentProvider, $location){
  return {
    restrict: 'E',
    scope: {
      id: '=id',
    },
    bindToController: true,
    controllerAs: 'vm',
    templateUrl: 'templates/cp_actions.html',
    controller: function(){
      this.deleteCp = function(id){
        ContentProvider.delete({id: id}).$promise
        .then(function(){
          $location.url('/');
        });
      };
    }
  };
})
.directive('contentProviderList', function(ContentProvider, _){
  return {
    restrict: 'E',
    controllerAs: 'vm',
    scope: {},
    templateUrl: 'templates/cp_list.html',
    controller: function(){
      ['Name', 'Description', 'Status', 'Actions']
      this.tableConfig = {
        columns: [
          {
            label: 'Name',
            field: 'humanReadableName'
          },
          {
            label: 'Description',
            field: 'description'
          },
          {
            label: 'Status',
            field: 'enabled'
          }
        ],
        enableActions: true
      };

      var self = this;

      ContentProvider.query().$promise
      .then(function(cp){
        self.contentProviderList = cp;
      })
      .catch(function(e){
        throw new Error(e);
      });

      this.deleteCp = function(id){
        ContentProvider.delete({id: id}).$promise
        .then(function(){
          _.remove(self.contentProviderList, {id: id});
        });
      };
    }
  };
})
.directive('contentProviderDetail', function(ContentProvider, ServiceProvider, $stateParams, $location){
  return {
    restrict: 'E',
    controllerAs: 'vm',
    scope: {},
    templateUrl: 'templates/cp_detail.html',
    controller: function(){
      this.pageName = 'detail';
      var self = this;

      if($stateParams.id){
        ContentProvider.get({id: $stateParams.id}).$promise
        .then(function(cp){
          self.cp = cp;
        }).catch(function(e){
          self.result = {
            status: 0,
            msg: e.data.detail
          };
        });
      }
      else{
        self.cp = new ContentProvider();
      }

      ServiceProvider.query().$promise
      .then(function(sp){
        self.sp = sp;
      });

      this.saveContentProvider = function(cp){
        var p, isNew = false;

        if(cp.id){
          p = cp.$update();
        }
        else{
          isNew = true;
          cp.name = cp.humanReadableName;
          p = cp.$save();
        }

        p.then(function(res){
          self.result = {
            status: 1,
            msg: 'Content Provider Saved'
          };
          if(isNew){
            $location.url('contentProvider/' + res.id + '/');
          }
        })
        .catch(function(e){
          self.result = {
            status: 0,
            msg: e.data.detail
          };
        });
      };
    }
  };
})
.directive('contentProviderCdn', function($stateParams, CdnPrefix, ContentProvider){
  return{
    restrict: 'E',
    controllerAs: 'vm',
    scope: {},
    templateUrl: 'templates/cp_cdn_prefix.html',
    controller: function(_){
      var self = this;

      this.pageName = 'cdn';

      if($stateParams.id){
        ContentProvider.get({id: $stateParams.id}).$promise
        .then(function(cp){
          self.cp = cp;
        }).catch(function(e){
          self.result = {
            status: 0,
            msg: e.data ? e.data.detail : ''
          };
        });
      }

      CdnPrefix.query().$promise
      .then(function(prf){
        self.prf = prf;
        // console.log(prf, $stateParams.id);
        // set the active CdnPrefix for this contentProvider
        self.cp_prf = [];
        self.cp_prf.push(_.find(prf, {contentProvider: parseInt($stateParams.id)}));
      }).catch(function(e){
        self.result = {
          status: 0,
          msg: e.data.detail
        };
      });

      this.addPrefix = function(prf){
        prf.contentProvider = $stateParams.id;

        var item = new CdnPrefix(prf);

        item.$save()
        .then(function(res){
          self.cp_prf.push(res);
        })
        .catch(function(e){
          self.result = {
            status: 0,
            msg: e.data.detail
          };
        });
      };

      this.removePrefix = function(item){
        item.$delete()
        .then(function(){
          _.remove(self.cp_prf, item);
        })
        .catch(function(e){
          self.result = {
            status: 0,
            msg: e.data.detail
          };
        });
      };
    }
  };
})
.directive('contentProviderServer', function($stateParams, OriginServer, ContentProvider){
  return{
    restrict: 'E',
    controllerAs: 'vm',
    scope: {},
    templateUrl: 'templates/cp_origin_server.html',
    controller: function(_){
      this.pageName = 'server';
      this.protocols = {'http': 'HTTP', 'rtmp': 'RTMP', 'rtp': 'RTP', 'shout': 'SHOUTcast'};

      var self = this;

      if($stateParams.id){
        ContentProvider.get({id: $stateParams.id}).$promise
        .then(function(cp){
          self.cp = cp;
        }).catch(function(e){
          self.result = {
            status: 0,
            msg: e.data.detail
          };
        });
      }

      OriginServer.query({contentProvider: $stateParams.id}).$promise
      .then(function(cp_os){
        self.cp_os = cp_os;
      }).catch(function(e){
        self.result = {
          status: 0,
          msg: e.data.detail
        };
      });

      this.addOrigin = function(os){
        os.contentProvider = $stateParams.id;

        var item = new OriginServer(os);

        item.$save()
        .then(function(res){
          self.cp_os.push(res);
        })
        .catch(function(e){
          self.result = {
            status: 0,
            msg: e.data.detail
          };
        });
      };

      this.removeOrigin = function(item){
        item.$delete()
        .then(function(){
          _.remove(self.cp_os, item);
        })
        .catch(function(e){
          self.result = {
            status: 0,
            msg: e.data.detail
          };
        });
      };
    }
  };
})
.directive('contentProviderUsers', function($stateParams, ContentProvider, User){
  return{
    restrict: 'E',
    controllerAs: 'vm',
    scope: {},
    templateUrl: 'templates/cp_user.html',
    controller: function(_){
      var self = this;

      this.pageName = 'user';

      this.cp_users = [];

      if($stateParams.id){
        User.query().$promise
        .then(function(users){
          self.users = users;
          return ContentProvider.get({id: $stateParams.id}).$promise;
        })
        .then(function(res){
          res.users = self.populateUser(res.users, self.users);
          return res;
        })
        .then(function(cp){
          self.cp = cp;
        }).catch(function(e){
          self.result = {
            status: 0,
            msg: e.data.detail
          };
        });
      }

      this.populateUser = function(ids, list){
        for(var i = 0; i < ids.length; i++){
          ids[i] = _.find(list, {id: ids[i]});
        }
        return ids;
      };

      this.addUserToCp = function(user){
        self.cp.users.push(user);
      };

      this.removeUserFromCp = function(user){
        _.remove(self.cp.users, user);
      };

      this.saveContentProvider = function(cp){

        // flatten the user to id of array
        cp.users = _.map(cp.users, 'id');

        cp.$update()
        .then(function(res){

          self.cp.users = self.populateUser(res.users, self.users);

          self.result = {
            status: 1,
            msg: 'Content Provider Saved'
          };

        })
        .catch(function(e){
          self.result = {
            status: 0,
            msg: e.data.detail
          };
        });
      };
    }
  };
});