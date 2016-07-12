(function() {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Dashboards
  * @description Angular resource to fetch /api/core/dashboardviews/:id/
  **/
  .service('Dashboards', function($resource, $q, $http){
    const r = $resource('/api/core/dashboardviews/:id/', { id: '@id' }, {
      update: { method: 'PUT' }
    });

    r.prototype.$save = function(){
      const d = $q.defer();

      $http.put(`/api/core/dashboardviews/${this.id}/`, this)
      .then((res) => {
        d.resolve(res.data);
      })
      .catch(e => {
        d.reject(e.data);
      });

      return d.promise;
    }

    return r;
  })
})();