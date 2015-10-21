/* global angular */
/* eslint-disable dot-location*/

angular.module('contentProviderApp', [
  'ngResource',
  'ngRoute'
])
.config(function($interpolateProvider, $routeProvider) {
  $interpolateProvider.startSymbol('{$');
  $interpolateProvider.endSymbol('$}');

  $routeProvider
  .when('/', {
    template: '<content-provider-list></content-provider-list>',
  })
  .when('/contentProvider/:id', {
    template: '<content-provider-detail></content-provider-detail>'
  })
  .otherwise('/');
})
.service('ContentProvider', function($resource) {
  return $resource('/hpcapi/contentproviders/:id', {id: '@id'});
})
.service('ServiceProvider', function($resource) {
  return $resource('/hpcapi/serviceproviders/:id', {id: '@id'});
})
.directive('contentProviderList', function(ContentProvider) {
  return {
    restrict: 'E',
    controllerAs: 'vm',
    templateUrl: '../../static/templates/contentProvider/cp_list.html',
    controller: function() {
      var _this = this;

      ContentProvider.query().$promise
      .then(function(cp) {
        _this.contentProviderList = cp;
      })
      .catch(function(e) {
        throw new Error(e);
      });
    }
  };
})
.directive('contentProviderDetail', function(ContentProvider, ServiceProvider, $routeParams) {
  return {
    restrict: 'E',
    controllerAs: 'vm',
    templateUrl: '../../static/templates/contentProvider/cp_detail.html',
    controller: function() {
      var _this = this;

      ContentProvider.get({id: $routeParams.id}).$promise
      .then(function(cp) {
        _this.cp = cp;
      });

      ServiceProvider.query().$promise
      .then(function(sp) {
        _this.sp = sp;
      });

      // check if the list id match with item url
      this.activeServiceProvide = function(id, SPurl) {
        if(SPurl && SPurl.length > 0) {
          // take the last 2 char and remove trailing /
          return parseInt(SPurl.substr(SPurl.length - 2).replace('/','')) === id;
        }
        return false;
      };
    }
  };
});