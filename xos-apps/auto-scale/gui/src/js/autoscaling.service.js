'use strict';

angular.module('autoscaling')
.service('Autoscaling', function($http, $interval, $rootScope){

  const pollingFrequency = 1;
  var pollinginterval;

  this.getAutoscalingData = () => {
    pollinginterval = $interval(() => {
      $http.get('/autoscaledata')
      .then((res) => {
        $rootScope.$emit('autoscaling.update', res.data);
      });
    }, pollingFrequency * 1000)
  };
});