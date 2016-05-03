/**
 * © OpenCORD
 *
 * Visit http://guide.xosproject.org/devguide/addview/ for more information
 *
 * Created by teone on 3/24/16.
 */

(function () {
  'use strict';

  angular.module('xos.uiComponents')
  /**
    * @ngdoc directive
    * @name xos.uiComponents.directive:xosSmartPie
    * @restrict E
    * @description The xos-table directive
    * @param {Object} config The configuration for the component,
    * it is composed by the name of an angular [$resource](https://docs.angularjs.org/api/ngResource/service/$resource)
    * and a field name that is used to group the data.
    * ```
    * {
        resource: 'Users',
        groupBy: 'fieldName',
        classes: 'my-custom-class',
      }
    * ```
    * @scope
    * @example
    */
  .directive('xosSmartPie', function(){
    return {
      restrict: 'E',
      scope: {
        config: '='
      },
      template: `
        <canvas
          class="chart chart-pie {{vm.config.classes}}"
          chart-data="vm.data" chart-labels="vm.labels">
        </canvas>
      `,
      bindToController: true,
      controllerAs: 'vm',
      controller: function($injector, _){
        this.Resource = $injector.get(this.config.resource);

        const getData = () => {
          this.Resource.query().$promise
          .then((res) => {

            if(!res[0]){
              return;
            }

            // group data
            let grouped = _.groupBy(res, this.config.groupBy);
            this.data = _.reduce(Object.keys(grouped), (data, group) => data.concat(grouped[group].length), []);

            // create labels
            this.labels = Object.keys(grouped);
          });
        }

        getData();
      }
    };
  });
})();
