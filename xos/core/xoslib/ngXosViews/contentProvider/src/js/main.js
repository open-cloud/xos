/* global angular */
/* eslint-disable dot-location*/

// TODO
// - Add Cache
// - Refactor routing with ui.router and child views (share the navigation and header)

'use strict';

angular.module('xos.contentProvider', [
  'ngResource',
  'ngRoute',
  'ngCookies',
  'ngLodash',
  'xos.helpers',
  'xos.xos'
])
.config(($routeProvider) => {

  $routeProvider
  .when('/', {
    template: '<content-provider-list></content-provider-list>',
  })
  .when('/contentProvider/:id?', {
    template: '<content-provider-detail></content-provider-detail>'
  })
  .when('/contentProvider/:id/cdn_prefix', {
    template: '<content-provider-cdn></content-provider-cdn>'
  })
  .when('/contentProvider/:id/origin_server', {
    template: '<content-provider-server></content-provider-server>'
  })
  .when('/contentProvider/:id/users', {
    template: '<content-provider-users></content-provider-users>'
  })
  .otherwise('/');
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
.directive('contentProviderList', function(ContentProvider, lodash){
  return {
    restrict: 'E',
    controllerAs: 'vm',
    scope: {},
    templateUrl: 'templates/cp_list.html',
    controller: function(){
      var _this = this;

      ContentProvider.query().$promise
      .then(function(cp){
        _this.contentProviderList = cp;
      })
      .catch(function(e){
        throw new Error(e);
      });

      this.deleteCp = function(id){
        ContentProvider.delete({id: id}).$promise
        .then(function(){
          lodash.remove(_this.contentProviderList, {id: id});
        });
      };
    }
  };
})
.directive('contentProviderDetail', function(ContentProvider, ServiceProvider, $routeParams, $location){
  return {
    restrict: 'E',
    controllerAs: 'vm',
    scope: {},
    templateUrl: 'templates/cp_detail.html',
    controller: function(){
      this.pageName = 'detail';
      var _this = this;

      if($routeParams.id){
        ContentProvider.get({id: $routeParams.id}).$promise
        .then(function(cp){
          _this.cp = cp;
        }).catch(function(e){
          _this.result = {
            status: 0,
            msg: e.data.detail
          };
        });
      }
      else{
        _this.cp = new ContentProvider();
      }

      ServiceProvider.query().$promise
      .then(function(sp){
        _this.sp = sp;
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
          _this.result = {
            status: 1,
            msg: 'Content Provider Saved'
          };
          if(isNew){
            $location.url('contentProvider/' + res.id + '/');
          }
        })
        .catch(function(e){
          _this.result = {
            status: 0,
            msg: e.data.detail
          };
        });
      };
    }
  };
})
.directive('contentProviderCdn', function($routeParams, CdnPrefix, ContentProvider, lodash){
  return{
    restrict: 'E',
    controllerAs: 'vm',
    scope: {},
    templateUrl: 'templates/cp_cdn_prefix.html',
    controller: function(){
      var _this = this;

      this.pageName = 'cdn';

      if($routeParams.id){
        ContentProvider.get({id: $routeParams.id}).$promise
        .then(function(cp){
          _this.cp = cp;
        }).catch(function(e){
          _this.result = {
            status: 0,
            msg: e.data.detail
          };
        });
      }

      CdnPrefix.query().$promise
      .then(function(prf){
        _this.prf = prf;
        // set the active CdnPrefix for this contentProvider
        _this.cp_prf = lodash.where(prf, {contentProvider: parseInt($routeParams.id)});
      }).catch(function(e){
        _this.result = {
          status: 0,
          msg: e.data.detail
        };
      });

      this.addPrefix = function(prf){
        prf.contentProvider = $routeParams.id;

        var item = new CdnPrefix(prf);

        item.$save()
        .then(function(res){
          _this.cp_prf.push(res);
        })
        .catch(function(e){
          _this.result = {
            status: 0,
            msg: e.data.detail
          };
        });
      };

      this.removePrefix = function(item){
        item.$delete()
        .then(function(){
          lodash.remove(_this.cp_prf, item);
        })
        .catch(function(e){
          _this.result = {
            status: 0,
            msg: e.data.detail
          };
        });
      };
    }
  };
})
.directive('contentProviderServer', function($routeParams, OriginServer, ContentProvider, lodash){
  return{
    restrict: 'E',
    controllerAs: 'vm',
    scope: {},
    templateUrl: 'templates/cp_origin_server.html',
    controller: function(){
      this.pageName = 'server';
      this.protocols = {'http': 'HTTP', 'rtmp': 'RTMP', 'rtp': 'RTP','shout': 'SHOUTcast'};

      var _this = this;

      if($routeParams.id){
        ContentProvider.get({id: $routeParams.id}).$promise
        .then(function(cp){
          _this.cp = cp;
        }).catch(function(e){
          _this.result = {
            status: 0,
            msg: e.data.detail
          };
        });
      }

      OriginServer.query({contentProvider: $routeParams.id}).$promise
      .then(function(cp_os){
        _this.cp_os = cp_os;
      }).catch(function(e){
        _this.result = {
          status: 0,
          msg: e.data.detail
        };
      });

      this.addOrigin = function(os){
        os.contentProvider = $routeParams.id;

        var item = new OriginServer(os);

        item.$save()
        .then(function(res){
          _this.cp_os.push(res);
        })
        .catch(function(e){
          _this.result = {
            status: 0,
            msg: e.data.detail
          };
        });
      };

      this.removeOrigin = function(item){
        item.$delete()
        .then(function(){
          lodash.remove(_this.cp_os, item);
        })
        .catch(function(e){
          _this.result = {
            status: 0,
            msg: e.data.detail
          };
        });
      };
    }
  };
})
.directive('contentProviderUsers', function($routeParams, ContentProvider, User, lodash){
  return{
    restrict: 'E',
    controllerAs: 'vm',
    scope: {},
    templateUrl: 'templates/cp_user.html',
    controller: function(){
      var _this = this;

      this.pageName = 'user';

      this.cp_users = [];

      if($routeParams.id){
        User.query().$promise
        .then(function(users){
          _this.users = users;
          return ContentProvider.get({id: $routeParams.id}).$promise;
        })
        .then(function(res){
          res.users = _this.populateUser(res.users, _this.users);
          return res;
        })
        .then(function(cp){
          _this.cp = cp;
        }).catch(function(e){
          _this.result = {
            status: 0,
            msg: e.data.detail
          };
        });
      }

      this.populateUser = function(ids, list){
        for(var i = 0; i < ids.length; i++){
          ids[i] = lodash.find(list, {id: ids[i]});
        }
        return ids;
      };

      this.addUserToCp = function(user){
        _this.cp.users.push(user);
      };

      this.removeUserFromCp = function(user){
        lodash.remove(_this.cp.users, user);
      };

      this.saveContentProvider = function(cp){

        // flatten the user to id of array
        cp.users = lodash.pluck(cp.users, 'id');

        cp.$update()
        .then(function(res){

          _this.cp.users = _this.populateUser(res.users, _this.users);

          _this.result = {
            status: 1,
            msg: 'Content Provider Saved'
          };

        })
        .catch(function(e){
          _this.result = {
            status: 0,
            msg: e.data.detail
          };
        });
      };
    }
  };
});