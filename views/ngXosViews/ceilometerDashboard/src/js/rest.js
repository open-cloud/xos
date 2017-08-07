
/*
 * Copyright 2017-present Open Networking Foundation

 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at

 * http://www.apache.org/licenses/LICENSE-2.0

 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */


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

        $http.get('/api/tenant/monitoring/dashboard/xos-slice-service-mapping/')
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

        $http.get('/api/tenant/monitoring/dashboard/meters/', {cache: true, params: params})
          // $http.get('../meters_mock.json', {cache: true})
          .then((res) => {
            deferred.resolve(res.data)
          })
          .catch((e) => {
            deferred.reject(e);
          });

        return deferred.promise;
      };

      this.getSamples = (name, limit = 10) => {
        let deferred = $q.defer();

        $http.get(`/api/tenant/monitoring/dashboard/metersamples/`, {params: {meter: name, limit: limit}})
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

        $http.get('/api/tenant/monitoring/dashboard/meterstatistics/', {cache: true, params: options})
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

