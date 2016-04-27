/**
 * © OpenCORD
 *
 * Visit http://guide.xosproject.org/devguide/addview/ for more information
 *
 * Created by teone on 4/18/16.
 */

(function () {
  'use strict';

  angular.module('xos.uiComponents')

  /**
    * @ngdoc directive
    * @name xos.uiComponents.directive:xosForm
    * @restrict E
    * @description The xos-form directive
    * @param {Object} config The configuration object
    * ```
    * {
    *   exclude: ['id', 'validators', 'created', 'updated', 'deleted'], //field to be skipped in the form, the provide values are concatenated
    *   actions: [ // define the form buttons with related callback
    *     {
            label: 'save',
            icon: 'ok', // refers to bootstraps glyphicon
            cb: (user) => { // receive the model
              console.log(user);
            },
            class: 'success'
          }
    *   ]
    * }
    * ```
    * @element ANY
    * @scope
    * @example
  <example module="sampleForm">
    <file name="index.html">
      <div ng-controller="SampleCtrl as vm">
        <xos-form ng-model="vm.model" config="vm.config"></xos-form>
      </div>
    </file>
    <file name="script.js">
      angular.module('sampleForm', ['xos.uiComponents'])
      .factory('_', function($window){
        return $window._;
      })
      .controller('SampleCtrl', function(){
        this.model = {
          first_name: 'Jhon',
          last_name: 'Doe',
          email: 'jhon.doe@sample.com',
          active: true,
          birthDate: '2015-02-17T22:06:38.059000Z'
        }
        this.config = {
          exclude: ['password', 'last_login'],
          formName: 'sampleForm',
          actions: [
            {
              label: 'Save',
              icon: 'ok', // refers to bootstraps glyphicon
              cb: (user) => { // receive the model
                console.log(user);
              },
              class: 'success'
            }
          ]
        };
      });
    </file>
  </example>

  **/

  .directive('xosForm', function(){
    return {
      restrict: 'E',
      scope: {
        config: '=',
        ngModel: '='
      },
      template: `
        <ng-form name="vm.{{vm.config.formName || 'form'}}">
          <div class="form-group" ng-repeat="(name, field) in vm.formField">
            <label>{{field.label}}</label>
            <input
              ng-if="field.type !== 'boolean'"
              type="{{field.type}}"
              name="{{name}}"
              class="form-control"
              ng-model="vm.ngModel[name]"
              ng-minlength="field.validators.minlength || 0"
              ng-maxlength="field.validators.maxlength || 2000"
              ng-required="field.validators.required || false" />
            <span class="boolean-field" ng-if="field.type === 'boolean'">
              <button
                class="btn btn-success"
                ng-show="vm.ngModel[name]"
                ng-click="vm.ngModel[name] = false">
                <i class="glyphicon glyphicon-ok"></i>
              </button>
              <button
                class="btn btn-danger"
                ng-show="!vm.ngModel[name]"
                ng-click="vm.ngModel[name] = true">
                <i class="glyphicon glyphicon-remove"></i>
              </button>
            </span>
            <!-- <pre>{{vm[vm.config.formName][name].$error | json}}</pre> -->
            <xos-validation errors="vm[vm.config.formName || 'form'][name].$error"></xos-validation>
          </div>
          <div class="form-group" ng-if="vm.config.actions">
            <button role="button" href=""
              ng-repeat="action in vm.config.actions"
              ng-click="action.cb(vm.ngModel)"
              class="btn btn-{{action.class}}"
              title="{{action.label}}">
              <i class="glyphicon glyphicon-{{action.icon}}"></i>
              {{action.label}}
            </button>
          </div>
        </ng-form>
      `,
      bindToController: true,
      controllerAs: 'vm',
      controller: function($scope, $log, _, XosFormHelpers){

        if(!this.config){
          throw new Error('[xosForm] Please provide a configuration via the "config" attribute');
        }

        if(!this.config.actions){
          throw new Error('[xosForm] Please provide an action list in the configuration');
        }

        this.excludedField = ['id', 'validators', 'created', 'updated', 'deleted', 'backend_status'];
        if(this.config && this.config.exclude){
          this.excludedField = this.excludedField.concat(this.config.exclude);
        }


        this.formField = [];
        $scope.$watch(() => this.ngModel, (model) => {

          // empty from old stuff
          this.formField = {};

          if(!model){
            return;
          }

          let diff = _.difference(Object.keys(model), this.excludedField);
          let modelField = XosFormHelpers.parseModelField(diff);
          this.formField = XosFormHelpers.buildFormStructure(modelField, this.config.fields, model);
        });

      }
    }
  })
  .service('XosFormHelpers', function(_, LabelFormatter){

    this._isEmail = (text) => {
      var re = /(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))/;
      return re.test(text);
    };

    this._getFieldFormat = (value) => {

      // check if is date
      if (_.isDate(value) || (!Number.isNaN(Date.parse(value)) && new Date(value).getTime() > 631180800000)){
        return 'date';
      }

      // check if is boolean
      // isNaN(false) = false, false is a number (0), true is a number (1)
      if(typeof value  === 'boolean'){
        return 'boolean';
      }

      // check if a string is a number
      if(!isNaN(value) && value !== null){
        return 'number';
      }

      // check if a string is an email
      if(this._isEmail(value)){
        return 'email';
      }

      // if null return string
      if(value === null){
        return 'string';
      }

      return typeof value;
    };

    this.buildFormStructure = (modelField, customField, model) => {

      // console.log(modelField, model);

      modelField = Object.keys(modelField).length > 0 ? modelField : customField; //if no model field are provided, check custom
      customField = customField || {};

      return _.reduce(Object.keys(modelField), (form, f) => {

        form[f] = {
          label: (customField[f] && customField[f].label) ? `${customField[f].label}:` : LabelFormatter.format(f),
          type: (customField[f] && customField[f].type) ? customField[f].type : this._getFieldFormat(model[f]),
          validators: (customField[f] && customField[f].validators) ? customField[f].validators : {}
        };

        if(form[f].type === 'date'){
          model[f] = new Date(model[f]);
        }

        if(form[f].type === 'number'){
          model[f] = parseInt(model[f], 10);
        }

        return form;
      }, {});
    };

    this.parseModelField = (fields) => {
      return _.reduce(fields, (form, f) => {
        form[f] = {};
        return form;
      }, {});
    }

  })
})();
