/**
 * © OpenCORD
 *
 * Visit http://guide.xosproject.org/devguide/addview/ for more information
 *
 * Created by teone on 3/21/16.
 */

(function () {
  'use strict';

  angular.module('xos.ceilometerDashboard')
    .service('Ceilometer', function($http, $q){

      this.getMappings = () => {
        let deferred = $q.defer();

        $http.get('/xoslib/xos-slice-service-mapping/')
          .then((res) => {
            deferred.resolve(res.data)
          })
          .catch((e) => {
            deferred.reject(e);
          });

        return deferred.promise;
      };

      this.getMeters = (params) => {
        let deferred = $q.defer();

        $http.get('/xoslib/meters/', {cache: true, params: params})
          // $http.get('../meters_mock.json', {cache: true})
          .then((res) => {
            deferred.resolve(res.data)
          })
          .catch((e) => {
            deferred.reject(e);
          });

        return deferred.promise;
      };

      this.getSamples = (name, tenant) => {
        let deferred = $q.defer();

        $http.get(`/xoslib/metersamples/`, {params: {meter: name, tenant: tenant}})
          .then((res) => {
            deferred.resolve(res.data)
          })
          .catch((e) => {
            deferred.reject(e);
          });

        return deferred.promise;
      };

      this.getStats = (options) => {
        let deferred = $q.defer();

        $http.get('/xoslib/meterstatistics/', {cache: true, params: options})
          // $http.get('../stats_mock.son', {cache: true})
          .then((res) => {
            deferred.resolve(res.data);
          })
          .catch((e) => {
            deferred.reject(e);
          });

        return deferred.promise;
      };

      // hold dashboard status (opened service, slice, resource)
      this.selectedService = null;
      this.selectedSlice = null;
      this.selectedResource = null;
    });
})();

