(function() {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.SlicesPlus
  * @description Angular resource to fetch /api/utility/slicesplus/
  * This is a read-only API and only the `query` method is currently supported.
  **/
  .service('SlicesPlus', function($http, $q){
    this.query = (params) => {
      let deferred = $q.defer();

      $http.get('/api/utility/slicesplus/', {params: params})
      .then(res => {
        deferred.resolve(res.data);
      })
      .catch(res => {
        deferred.reject(res.data);
      });

      return {$promise: deferred.promise};
    }

    this.get = (id, params) => {
      let deferred = $q.defer();

      $http.get(`/api/utility/slicesplus/${id}`, {params: params})
      .then(res => {
        deferred.resolve(res.data);
      })
      .catch(res => {
        deferred.reject(res.data);
      });
      return {$promise: deferred.promise};
      
    }
  })
})();
