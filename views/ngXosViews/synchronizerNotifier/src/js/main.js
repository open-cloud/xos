'use strict';

angular.module('xos.synchronizerNotifier', [
  'ngResource',
  'ngCookies',
  'ui.router',
  'xos.helpers'
])
.config(function($provide) {
  $provide.decorator('$rootScope', function($delegate) {
    var Scope = $delegate.constructor;
    // var origBroadcast = Scope.prototype.$broadcast;
    // var origEmit = Scope.prototype.$emit;
    var origOn = Scope.prototype.$on;

    // Scope.prototype.$broadcast = function() {
    //   // console.log("$broadcast was called on $scope " + $scope.$id + " with arguments:", arguments);
    //   return origBroadcast.apply(this, arguments);
    // };
    // Scope.prototype.$emit = function() {
    //   // console.log("$emit was called on $scope " + $scope.$id + " with arguments:", arguments);
    //   return origEmit.apply(this, arguments);
    // };

    Scope.prototype.$on = function(){
      // console.log('$on', arguments, arguments[1].toString());
      return origOn.apply(this, arguments);
    }
    return $delegate;
  });
})
.service('Diag', function($rootScope, $http, $q, $interval){

  let isRunning = false;

  this.getDiags = () => {
    let d = $q.defer();
    $http.get('/api/core/diags')
    .then(res => {
      d.resolve(res.data);
    })
    .catch(err => {
      d.reject(err);
    });

    return d.promise;
  };

  this.sendEvents = (diags) => {
    diags.forEach(d => {
      let status = JSON.parse(d.backend_register);
      status.last_run = new Date(status.last_run * 1000);
      $rootScope.$broadcast(`diag`, {
        name: d.name,
        updated: d.updated,
        info: status,
        status: this.getSyncStatus(status)
      });
    });
  };

  this.start = () => {
    isRunning = true;
    this.getDiags()
    .then(diags => {
      this.sendEvents(diags);
    });
    return isRunning;
  };

  this.stop = () => {
    isRunning = false;
    return isRunning;
  };

  this.getSyncStatus = (status) => {

    let gap = 5 * 60 * 1000; /* ms */
    // let gap = 2;

    if (((new Date()) - status.last_run) > gap){
      return false;
    }
    return true;
  }

  $interval(() => {
    if(isRunning){
      this.getDiags()
      .then(diags => {
        this.sendEvents(diags);
      });
    }
  }, 25000);
})
.run(function($log){
  $log.info('Listening for Syncronizers Events!');
})
.directive('syncStatus', function() {
  return {
    restrict: 'E',
    scope: {},
    bindToController: true,
    controllerAs: 'vm',
    templateUrl: 'templates/sync-status.tpl.html',
    controller: function($log, $rootScope, Diag){
      Diag.start();
      // this.showNotificationPanel = true;
      this.synchronizers = {};

      this.showNoSync = true;

      $rootScope.$on('diag', (e, d) => {
        // $log.info('Received event: ', d);
        this.synchronizers[d.name] = d;
        this.showNoSync = false;
        if(Object.keys(this.synchronizers).length === 0){
          this.showNoSync = true;
        }
      });

    }
  }
});

angular.element(document).ready(function() {
  angular.bootstrap('#xosSynchronizerNotifier', ['xos.synchronizerNotifier']);
});