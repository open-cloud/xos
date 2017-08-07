
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
    .directive('ceilometerStats', function(){
      return {
        restrict: 'E',
        scope: {
          name: '=name',
          tenant: '=tenant'
        },
        bindToController: true,
        controllerAs: 'vm',
        templateUrl: 'templates/ceilometer-stats.tpl.html',
        controller: function($scope, Ceilometer) {

          this.getStats = (tenant) => {
            this.loader = true;
            Ceilometer.getStats({tenant: tenant})
              .then(res => {
                res.map(m => {
                  m.resource_name = m.resource_name.replace('mysite_onos_vbng', 'ONOS_FABRIC');
                  m.resource_name = m.resource_name.replace('mysite_onos_volt', 'ONOS_CORD');
                  m.resource_name = m.resource_name.replace('mysite_vbng', 'mysite_vRouter');
                  return m;
                });
                this.stats = res;
              })
              .catch(err => {
                this.error = err.data;
              })
              .finally(() => {
                this.loader = false;
              });
          };

          $scope.$watch(() => this.name, (val) => {
            if(val){
              this.getStats(this.tenant);
            }
          });
        }
      }
    });
})();

