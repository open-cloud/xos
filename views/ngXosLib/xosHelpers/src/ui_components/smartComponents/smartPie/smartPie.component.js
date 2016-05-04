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
        labelFormatter: (labels) => {
          // here you can format your label,
          // you should return an array with the same order
          return labels;
        }
      }
    * ```
    * @scope
    * @example
     <example module="sampleSmartPie">
      <file name="index.html">
        <div ng-controller="SampleCtrl as vm">
          <xos-smart-pie config="vm.config"></xos-smart-pie>
        </div>
      </file>
      <file name="script.js">
        angular.module('sampleSmartPie', ['xos.uiComponents', 'ngResource', 'ngMockE2E'])
        .controller('SampleCtrl', function(){
          this.config = {
            resource: 'SampleResource',
            groupBy: 'category',
            poll: 2,
            labelFormatter: (labels) => {
              return labels.map(l => l === '1' ? 'Active' : 'Banned');
            }
          };
        });
      </file>
      <file name="backend.js">
        angular.module('sampleSmartPie')
        .run(function($httpBackend, _){
          let mock = [
            [
              {id: 1, first_name: 'Jon', last_name: 'Snow', category: 1},
              {id: 2, first_name: 'Danaerys', last_name: 'Targaryen', category: 2},
              {id: 3, first_name: 'Aria', last_name: 'Stark', category: 1},
              {id: 3, first_name: 'Tyrion', last_name: 'Lannister', category: 1}
            ],

            [
              {id: 1, first_name: 'Jon', last_name: 'Snow', category: 1},
              {id: 2, first_name: 'Danaerys', last_name: 'Targaryen', category: 2},
              {id: 3, first_name: 'Aria', last_name: 'Stark', category: 2},
              {id: 3, first_name: 'Tyrion', last_name: 'Lannister', category: 2}
            ],

            [
              {id: 1, first_name: 'Jon', last_name: 'Snow', category: 1},
              {id: 2, first_name: 'Danaerys', last_name: 'Targaryen', category: 2},
              {id: 3, first_name: 'Aria', last_name: 'Stark', category: 1},
              {id: 3, first_name: 'Tyrion', last_name: 'Lannister', category: 2}
            ]
          ];
          $httpBackend.whenGET('/test').respond(function(method, url, data, headers, params) {
            return [200, mock[Math.round(Math.random() * 3)]];
          });
        })
        .factory('_', function($window){
          return $window._;
        })
        .service('SampleResource', function($resource){
          return $resource('/test/:id', {id: '@id'});
        })
      </file>
    </example>

    <example module="sampleSmartPiePoll">
      <file name="index.html">
        <div ng-controller="SampleCtrl as vm">
          <xos-smart-pie config="vm.config"></xos-smart-pie>
        </div>
      </file>
      <file name="script.js">
        angular.module('sampleSmartPiePoll', ['xos.uiComponents', 'ngResource', 'ngMockE2E'])
        .controller('SampleCtrl', function(){
          this.config = {
            resource: 'SampleResource',
            groupBy: 'category',
            labelFormatter: (labels) => {
              return labels.map(l => l === '1' ? 'North' : 'Dragon');
            }
          };
        });
      </file>
      <file name="backendPoll.js">
        angular.module('sampleSmartPiePoll')
        .run(function($httpBackend, _){
          let datas = [
            {id: 1, first_name: 'Jon', last_name: 'Snow', category: 1},
            {id: 2, first_name: 'Danaerys', last_name: 'Targaryen', category: 2},
            {id: 3, first_name: 'Aria', last_name: 'Stark', category: 1}
          ];

          $httpBackend.whenGET('/test').respond(200, datas)
        })
        .factory('_', function($window){
          return $window._;
        })
        .service('SampleResource', function($resource){
          return $resource('/test/:id', {id: '@id'});
        })
      </file>
    </example>
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
          chart-data="vm.data" chart-labels="vm.labels"
          chart-legend="{{vm.config.legend}}">
        </canvas>
      `,
      bindToController: true,
      controllerAs: 'vm',
      controller: function($injector, $timeout, $interval, _){

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
            this.labels = angular.isFunction(this.config.labelFormatter) ? this.config.labelFormatter(Object.keys(grouped)) : Object.keys(grouped);
          });
        }

        getData();

        if(this.config.poll){
          $interval(() => {getData()}, this.config.poll * 1000)
        }
      }
    };
  });
})();
