'use strict';

angular.module('xos.vpnDashboard', [
  'ngResource',
  'ngCookies',
  'ngLodash',
  'ui.router',
  'xos.helpers'
])
.config(($stateProvider) => {
  $stateProvider
  .state('vpn-list', {
    url: '/',
    template: '<vpn-list></vpn-list>'
  });
})
.service('Vpn', function($http, $q){

  this.getVpnTenants = () => {
    let deferred = $q.defer();

    $http.get('/xoslib/vpntenants/')
    .then((res) => {
      deferred.resolve(res.data)
    })
    .catch((e) => {
      deferred.reject(e);
    });

    return deferred.promise;
  };
})
.config(function($httpProvider){
  $httpProvider.interceptors.push('NoHyperlinks');
})
.directive('vpnList', function(){
  return {
    restrict: 'E',
    scope: {},
    bindToController: true,
    controllerAs: 'vm',
    templateUrl: 'templates/vpn-list.tpl.html',
    controller: function(Vpn){
      // retrieving user list
      Vpn.getVpnTenants()
      .then((vpns) => {
        this.vpns = vpns;
      })
      .catch((e) => {
        throw new Error(e);
      });
    }
  };
});
