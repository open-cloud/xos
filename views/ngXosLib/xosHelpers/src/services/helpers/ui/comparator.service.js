(function() {
  'use strict';

  /**
   * @ngdoc service
   * @name xos.uiComponents.Comparator
   * @description
   * This factory define a function that replace the native angular.filter comparator.
   *
   * It is done to allow the comparation between (0|1) values with booleans.
   * >Note that this factory return a single function, not an object.
   *
   * The tipical usage of this factory is inside an `ng-repeat`
   * @example
   * <example module="comparator">
   *   <file name="index.html">
   *     <div ng-controller="sample as vm">
   *       <div class="row">
   *         <div class="col-xs-6">
   *           <label>Filter by name:</label>
   *           <input class="form-control" type="text" ng-model="vm.query.name"/>
   *         </div>
   *         <div class="col-xs-6">
   *           <label>Filter by status:</label>
   *           <select
   *            ng-model="vm.query.status"
   *            ng-options="i for i in [true, false]">
   *           </select>
   *         </div>
   *       </div>
   *       <div ng-repeat="item in vm.data | filter:vm.query:vm.comparator">
   *         <div class="row">
   *           <div class="col-xs-6">{{item.name}}</div>
   *           <div class="col-xs-6">{{item.status}}</div>
   *         </div>
   *       </div>
   *     </div>
   *   </file>
   *   <file name="script.js">
   *     angular.module('comparator', ['xos.uiComponents'])
   *     .controller('sample', function(Comparator){
   *       this.comparator = Comparator;
   *       this.data = [
   *         {name: 'Jhon', status: 1},
   *         {name: 'Jack', status: 0},
   *         {name: 'Mike', status: 1},
   *         {name: 'Scott', status: 0}
   *       ];
   *     });
   *   </file>
   * </example>
   **/

  angular
    .module('xos.uiComponents')
    .factory('Comparator', comparator);

  function comparator() {

    return function(actual, expected){

      if (angular.isUndefined(actual)) {
        // No substring matching against `undefined`
        return false;
      }
      if ((actual === null) || (expected === null)) {
        // No substring matching against `null`; only match against `null`
        return actual === expected;
      }
      if (angular.isObject(expected) || (angular.isObject(actual))){
        return angular.equals(expected, actual);
      }

      if(_.isBoolean(actual) || _.isBoolean(expected)){
        if(actual === 0 || actual === 1){
          actual = !!actual;
        }
        return angular.equals(expected, actual);
      }

      if(!angular.isString(actual) || !angular.isString(expected)){
        if(angular.isDefined(actual.toString) && angular.isDefined(expected.toString)){
          actual = actual.toString();
          expected = expected.toString();
        }
        else {
          return actual === expected;
        }
      }

      actual = actual.toLowerCase() + '';
      expected = expected.toLowerCase() + '';
      return actual.indexOf(expected) !== -1;
    };
  }
})();
