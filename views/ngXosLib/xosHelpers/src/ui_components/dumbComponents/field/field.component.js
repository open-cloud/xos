/**
 * © OpenCORD
 *
 * Visit http://guide.xosproject.org/devguide/addview/ for more information
 *
 * Created by teone on 5/25/16.
 */

(function () {
  'use strict';

  angular.module('xos.uiComponents')
  /**
    * @ngdoc directive
    * @name xos.uiComponents.directive:xosField
    * @restrict E
    * @description The xos-field directive.
    * This component decide, give a field wich kind of input it need to print.
    * @param {string} name The field name
    * @param {object} field The field configuration:
    * ```
    * {
    *   label: 'Label',
    *   type: 'number', //typeof field
    *   validators: {} // see xosForm for more details
    * }
    * ```
    * @param {mixed} ngModel The field value
    *
    * @example
    
    # Basic Example
    
      <example module="sampleField1">
        <file name="script.js">
          angular.module('sampleField1', ['xos.uiComponents'])
          .factory('_', function($window){
            return $window._;
          })
          .controller('SampleCtrl', function(){
            this.name = 'input-name';
            this.field = {label: 'My String Value:', type: 'string'};
            this.model = 'my string';
          });
        </file>
        <file name="index.html">
          <div ng-controller="SampleCtrl as vm">
            <xos-field ng-model="vm.model" name="vm.name" field="vm.field"></xos-field>
          </div>
        </file>
      </example>
      
      # Possible Values

      <example module="sampleField2">
        <file name="script.js">
          angular.module('sampleField2', ['xos.uiComponents'])
          .factory('_', function($window){
            return $window._;
          })
          .controller('SampleCtrl', function(){
            this.field1 = {
              name: 'number-field',
              field: {label: 'My Number Value:', type: 'number'},
              model: 2
            };

            this.field2 = {
              name: 'date-field',
              field: {label: 'My Date Value:', type: 'date'},
              model: new Date()
            };

            this.field3 = {
              name: 'boolean-field',
              field: {label: 'My Boolean Value:', type: 'boolean'},
              model: true
            };

            this.field4 = {
              name: 'email-field',
              field: {label: 'My Email Value:', type: 'email'},
              model: 'sample@domain.us'
            };
          });
        </file>
        <file name="index.html">
          <div ng-controller="SampleCtrl as vm">
            <xos-field ng-model="vm.field1.model" name="vm.field1.name" field="vm.field1.field"></xos-field>
            <xos-field ng-model="vm.field2.model" name="vm.field2.name" field="vm.field2.field"></xos-field>
            <xos-field ng-model="vm.field3.model" name="vm.field3.name" field="vm.field3.field"></xos-field>
            <xos-field ng-model="vm.field4.model" name="vm.field4.name" field="vm.field4.field"></xos-field>
          </div>
        </file>
      </example>

      # This element is recursive

      <example module="sampleField3">
        <file name="script.js">
          angular.module('sampleField3', ['xos.uiComponents'])
          .factory('_', function($window){
            return $window._;
          })
          .controller('SampleCtrl', function(){
            this.name = 'input-name';
            this.field = {label: 'My Object Value:', type: 'object'};
            this.model = {
              name: 'Jhon',
              age: '25',
              email: 'jhon@thewall.ru',
              active: true
            };
          });
        </file>
        <file name="index.html">
          <div ng-controller="SampleCtrl as vm">
            <xos-field ng-model="vm.model" name="vm.name" field="vm.field"></xos-field>
          </div>
        </file>
      </example>
    */
  .directive('xosField', function(RecursionHelper){
    return {
      restrict: 'E',
      scope: {
        name: '=',
        field: '=',
        ngModel: '='
      },
      template: `
        <label ng-if="vm.field.type !== 'object'">{{vm.field.label}}</label>
            <input
              ng-if="vm.field.type !== 'boolean' && vm.field.type !== 'object'"
              type="{{vm.field.type}}"
              name="{{vm.name}}"
              class="form-control"
              ng-model="vm.ngModel"
              ng-minlength="vm.field.validators.minlength || 0"
              ng-maxlength="vm.field.validators.maxlength || 2000"
              ng-required="vm.field.validators.required || false" />
            <span class="boolean-field" ng-if="vm.field.type === 'boolean'">
              <button
                class="btn btn-success"
                ng-show="vm.ngModel"
                ng-click="vm.ngModel = false">
                <i class="glyphicon glyphicon-ok"></i>
              </button>
              <button
                class="btn btn-danger"
                ng-show="!vm.ngModel"
                ng-click="vm.ngModel = true">
                <i class="glyphicon glyphicon-remove"></i>
              </button>
            </span>
            <div
              class="panel panel-default object-field"
              ng-if="vm.field.type == 'object' && !vm.isEmptyObject(vm.ngModel)"
              >
              <div class="panel-heading">{{vm.field.label}}</div>
              <div class="panel-body">
                <div ng-repeat="(k, v) in vm.ngModel">
                  <xos-field
                    name="k"
                    field="{label: vm.formatLabel(k), type: vm.getType(v)}"
                    ng-model="v">
                  </xos-field>
                </div>
              </div>
            </div>
      `,
      bindToController: true,
      controllerAs: 'vm',
      // the compile cicle is needed to support recursion
      compile: function (element) {
        return RecursionHelper.compile(element);
      },
      controller: function($attrs, XosFormHelpers, LabelFormatter){
        // console.log('Field: ', this.name, this.field, this.ngModel);
        if(!this.name){
          throw new Error('[xosField] Please provide a field name');
        }
        if(!this.field){
          throw new Error('[xosField] Please provide a field definition');
        }
        if(!$attrs.ngModel){
          throw new Error('[xosField] Please provide an ng-model');
        }

        this.getType = XosFormHelpers._getFieldFormat;
        this.formatLabel = LabelFormatter.format;

        this.isEmptyObject = o => Object.keys(o).length === 0;
      }
    }
  });
})();