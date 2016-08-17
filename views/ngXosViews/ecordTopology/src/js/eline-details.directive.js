/**
 * © OpenCORD
 *
 * Visit http://guide.xosproject.org/devguide/addview/ for more information
 *
 * Created by teone on 6/28/16.
 */

(function () {
  'use strict';
  angular.module('xos.ecordTopology')
  .directive('elineDetails', function() {
    return {
      restrict: 'E',
      scope: {
      },
      bindToController: true,
      controllerAs: 'vm',
      templateUrl: 'templates/eline-details.tpl.html',
      controller: function ($scope, $stateParams, Eline) {

        this.eline = null;

        const Resource = Eline();

        Eline.get({id: $stateParams.id}).$promise
        .then((eline) => {
          this.eline = eline;
        });

        this.slas = [
          {
            name: 'Latency',
            unit: 'ms',
            default: 300
          },
          {
            name: 'Latency Variation',
            unit: '%',
            default: 5
          },
          {
            name: 'Packet Loss',
            unit: '%',
            default: 2
          }
        ];

        this.availableServices = {
          performance: [
            {id: 1, label: 'WAN Accelerator'},
            {id: 2, label: 'Traffic Analytics'},
            {id: 3, label: 'Policy Control'},
          ],
          security: [
            {id: 4, label: 'Firewall'},
            {id: 5, label: 'Anti-virus'},
            {id: 6, label: 'IDS'},
            {id: 7, label: 'Encryption'},
          ],
          enterprise: [
            {id: 8, label: 'vRouter'},
            {id: 9, label: 'NAT'},
            {id: 10, label: 'VPN'},
          ]
        };

        this.activeServices = [];
        this.toggleService = (service) => {
          let isSelected = this.activeServices.indexOf(service);
          if(isSelected !== -1){
            this.activeServices.splice(this.activeServices.indexOf(service), 1);
          }
          else {
            this.activeServices.push(service);
          }
        };

        this.isServiceActive = (service) => {
          let isSelected = this.activeServices.indexOf(service);
          return (isSelected !== -1) ? true : false;
        };

        $scope.$watch(() => this.el, (val, oldval) => {
          if(val !== oldval && this.elineUpdate.$saved){
            this.eline.$saved = false;
          }
        }, true);

        this.saveEline = () => {

          const resource = new Eline(this.eline);

          resource.$save()
          .then(() => {
            $scope.saved = true;
          })
          .catch(e => {
            console.error(e);
          });
        };
      }
    }
  })
  .directive('bToMb', function() {
    // TODO improve with this:
    // https://gist.github.com/thomseddon/3511330
    return {
      require: 'ngModel',
      restrict: 'A',
      link: function(scope, element, attrs, ngModelController) {
        ngModelController.$parsers.push(function(data) {
          //convert data from view format to model format
          return data * 1000000000; //converted
        });

        ngModelController.$formatters.push(function(data) {
          //convert data from model format to view format
          return data / 1000000000; //converted
        });
      }
    }
  });
})();

