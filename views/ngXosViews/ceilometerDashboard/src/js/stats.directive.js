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

