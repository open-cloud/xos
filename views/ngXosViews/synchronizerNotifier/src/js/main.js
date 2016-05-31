'use strict';

angular.module('xos.synchronizerNotifier', [
  'ngResource',
  'ngCookies',
  'ui.router',
  'xos.helpers'
])
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
      status.last_duration = status.last_duration * 1000;
      status.last_synchronizer_start = new Date(status.last_synchronizer_start * 1000);
      status.last_syncrecord_start = status.last_syncrecord_start ? new Date(status.last_syncrecord_start * 1000) : null;
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

    // let gap = 5 * 60 * 1000; /* ms */
    let gap = 1 * 60 * 1000;
    // if(status.last_run > status.last_synchronizer_start){
    //   // the synchronizer has finished
    //   return true;
    // }
    // else {
      // the synchronizer is running
      // if(status.last_syncrecord_start){
      //   // but no step have been completed
      //   return false;
      // }
      // else
      if (((new Date()) - status.last_syncrecord_start) > gap){
        return false;
      }
      else{
        return true;
      }
    // }
  }

  $interval(() => {
    if(isRunning){
      this.getDiags()
      .then(diags => {
        this.sendEvents(diags);
      });
    }
  }, 10000);
})
.directive('syncStatus', function() {
  return {
    restrict: 'E',
    scope: {},
    bindToController: true,
    controllerAs: 'vm',
    templateUrl: 'templates/sync-status.tpl.html',
    controller: function($log, $rootScope, Diag, xosNotification){
      Diag.start();
      this.showNotificationPanel = true;
      this.synchronizers = {};

      const notified = {};

      // xosNotification.notify('test', {icon: 'http://localhost:8888/static/cord-logo.png', body: 'Diag'});

      this.showNoSync = true;

      $rootScope.$on('diag', (e, d) => {
        // console.log(d.name);
        if(d.name === 'global'){
          $log.info('Received event: ', d.info.last_syncrecord_start);
        }
        this.synchronizers[d.name] = d;

        if(!d.status){
          
          if(!notified[d.name]){
            console.log('sent notify');
            xosNotification.notify('CORD Synchronizer Error', {
              icon: 'http://localhost:8888/static/cord-logo.png',
              body: `[DEBUG] The ${d.name} synchronizer has stopped.`
            });
          }

          notified[d.name] = true;
        }
        else {
          notified[d.name] = false;
        }

        // hide list if empty
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