'use strict';

angular.module('autoscaling')
.service('Autoscaling', function($http, $interval, $rootScope, lodash, $q){

  const pollingFrequency = 10;
  var pollinginterval;

  /**
  * Convert data to a flat array of resources
  */

  this.formatData = (data) => {
    const list = [];
    // cicle trough all slices
    lodash.map(data, (item) => {
      // cicle trough every resource
      item.resources = lodash.forEach(
        Object.keys(item.resources),
        (resource) => {
          const tmp = item.resources[resource];
          tmp.service = item.service;
          tmp.slice = item.slice;
          tmp.project_id = item.project_id;
          tmp.instance_name = tmp.xos_instance_info.instance_name;
          delete tmp.xos_instance_info;
          list.push(tmp);
        }
      )
    });
    return list;
  };

  function requestData(url){

    const deferred = $q.defer();

    $http.get(url)
    .success((res) => {
      deferred.resolve(res);
    })
    .error((e) => {
      deferred.reject(e);
    });

    return deferred.promise;
  };


  // TODO Move to Websocket
  this.getAutoscalingData = () => {

    requestData('/autoscaledata')
    .then((res) => {
      $rootScope.$emit('autoscaling.update', this.formatData(res));
    })
    .catch((e) => {
      $rootScope.$emit('autoscaling.error', this.formatData(e));
    });

    pollinginterval = $interval(() => {
      requestData('/autoscaledata')
      .then((res) => {
        $rootScope.$emit('autoscaling.update', this.formatData(res));
      })
      .catch((e) => {
        $rootScope.$emit('autoscaling.error', this.formatData(e));
      });
    }, pollingFrequency * 1000)
  };
});