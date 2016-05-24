'use strict';

angular.module('xos.openVPNDashboard', [
  'ngResource',
  'ngCookies',
  'ui.router',
  'xos.helpers'
])
.config(($stateProvider) => {
  $stateProvider
  .state('openVPNList', {
    url: '/',
    template: '<vpn-list></vpn-list>'
  });
})
.config(($compileProvider) => {
  $compileProvider.aHrefSanitizationWhitelist(
    /^\s*(https?|ftp|mailto|tel|file|blob):/);
})
.service('Vpn', function($http, $q){

  this.getOpenVpnTenants = () => {
    let deferred = $q.defer();

    $http.get('/api/tenant/openvpn/list/')
    .then((res) => {
      deferred.resolve(res.data)
    })
    .catch((e) => {
      deferred.reject(e);
    });

    return deferred.promise;
  }
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
    templateUrl: 'templates/openvpn-list.tpl.html',
    controller: function(Vpn){
      Vpn.getOpenVpnTenants()
      .then((vpns) => {
        this.vpns = vpns;
        for (var i = 0; i < this.vpns.length; i++) {
          var blob = new Blob([this.vpns[i].script_text], {type: 'text/plain'});
          this.vpns[i].script_text = (window.URL || window.webkitURL).createObjectURL( blob );
        }
      })
      .catch((e) => {
        throw new Error(e);
      });
    }
  };
});
