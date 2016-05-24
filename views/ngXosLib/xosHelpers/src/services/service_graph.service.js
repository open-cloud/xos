(function() {
  'use strict';

  /**
  * @ngdoc service
  * @name xos.helpers.ServiceGraph
  * @description This factory define a set of helper function to query the service tenancy graph
  **/

  angular
  .module('xos.helpers')
  .service('GraphService', function($q, Tenants, Services) {

    this.loadCoarseData = () => {

      let services;

      let deferred = $q.defer();

      Services.query().$promise
      .then((res) => {
        services = res;
        return Tenants.query({kind: 'coarse'}).$promise;
      })
      .then((tenants) => {
        deferred.resolve({
          tenants: tenants,
          services: services
        });
      })

      return deferred.promise;
    }

    this.getCoarseGraph = () => {
      this.loadCoarseData()
      .then((res) => {
        console.log(res);
      })
      return 'ciao';
    };

  })
})();
