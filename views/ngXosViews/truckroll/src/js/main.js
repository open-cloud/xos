'use strict';

angular.module('xos.truckroll', [
  'ngResource',
  'ngCookies',
  'ui.router',
  'xos.helpers'
])
.config(($stateProvider) => {
  $stateProvider
  .state('user-list', {
    url: '/',
    template: '<truckroll></truckroll>'
  });
})
.config(function($httpProvider){
  $httpProvider.interceptors.push('NoHyperlinks');
})
.directive('truckroll', function(){
  return {
    restrict: 'E',
    scope: {},
    bindToController: true,
    controllerAs: 'vm',
    templateUrl: 'templates/truckroll.tpl.html',
    controller: function($timeout, $log, Subscribers, Truckroll){
      Subscribers.query().$promise
      .then((subscribers) => {
        this.subscribers = subscribers;
      });

      this.loader = false;

      this.runTest = () => {

        // clean previous tests
        delete this.truckroll.result;
        delete this.truckroll.is_synced;
        delete this.truckroll.result_code;
        delete this.truckroll.backend_status;

        const test = new Truckroll(this.truckroll);
        this.loader = true;
        test.$save()
        .then((res) => {
          this.waitForTest(res.id);
        })
      };

      this.waitForTest = (id) => {
        Truckroll.get({id: id}).$promise
        .then((testResult) => {
          // if error
          // or
          // if is synced
          if(
              testResult.backend_status.indexOf('2') >= 0 ||
              (testResult.result_code && testResult.result_code.indexOf('2') >= 0) ||
              testResult.is_synced
            ){
            this.truckroll = angular.copy(testResult);
            this.loader = false;
            Truckroll.delete({id: id});
          }
          // else keep polling
          else{
            $timeout(() => {
              this.waitForTest(id);
            }, 2000)
          }
        })
      };
    }
  };
});