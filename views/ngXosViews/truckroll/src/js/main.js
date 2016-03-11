'use strict';

angular.module('xos.truckroll', [
  'ngResource',
  'ngCookies',
  'ngLodash',
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
.service('Subscribers', function($resource){
  return $resource('/xos/subscribers/:id');
})
.service('Truckroll', function($resource){
  return $resource('/xoslib/truckroll/:id');
})
.directive('truckroll', function(){
  return {
    restrict: 'E',
    scope: {},
    bindToController: true,
    controllerAs: 'vm',
    templateUrl: 'templates/truckroll.tpl.html',
    controller: function($timeout, Subscribers, Truckroll){
      Subscribers.query().$promise
      .then((subscribers) => {
        this.subscribers = subscribers;
      });

      this.loader = false;

      this.runTest = () => {

        // clean previous tests
        delete this.truckroll.result;

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
          if(testResult.is_synced){
            this.truckroll = angular.copy(testResult);
            Truckroll.delete({id: id});
            this.loader = false;
          }
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