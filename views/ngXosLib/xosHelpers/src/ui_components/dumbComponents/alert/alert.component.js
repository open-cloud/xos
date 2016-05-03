/**
 * © OpenCORD
 *
 * Visit http://guide.xosproject.org/devguide/addview/ for more information
 *
 * Created by teone on 4/15/16.
 */

(function () {
  'use strict';

  angular.module('xos.uiComponents')

  /**
    * @ngdoc directive
    * @name xos.uiComponents.directive:xosAlert
    * @restrict E
    * @description The xos-alert directive
    * @param {Object} config The configuration object
    * ```
    * {
    *   type: 'danger', //info, success, warning
    *   closeBtn: true, //default false
    *   autoHide: 3000 //delay to automatically hide the alert
    * }
    * ```
    * @param {Boolean=} show Binding to show and hide the alert, default to true
    * @element ANY
    * @scope
    * @example
  <example module="sampleAlert1">
    <file name="index.html">
      <div ng-controller="SampleCtrl1 as vm">
        <xos-alert config="vm.config1">
          A sample alert message
        </xos-alert>
        <xos-alert config="vm.config2">
          A sample alert message (with close button)
        </xos-alert>
        <xos-alert config="vm.config3">
          A sample info message
        </xos-alert>
        <xos-alert config="vm.config4">
          A sample success message
        </xos-alert>
        <xos-alert config="vm.config5">
          A sample warning message
        </xos-alert>
      </div>
    </file>
    <file name="script.js">
      angular.module('sampleAlert1', ['xos.uiComponents'])
      .controller('SampleCtrl1', function(){
        this.config1 = {
          type: 'danger'
        };

        this.config2 = {
          type: 'danger',
          closeBtn: true
        };

        this.config3 = {
          type: 'info'
        };

        this.config4 = {
          type: 'success'
        };

        this.config5 = {
          type: 'warning'
        };
      });
    </file>
  </example>

  <example module="sampleAlert2" animations="true">
    <file name="index.html">
      <div ng-controller="SampleCtrl as vm" class="row">
        <div class="col-sm-4">
          <a class="btn btn-default btn-block" ng-show="!vm.show" ng-click="vm.show = true">Show Alert</a>
          <a class="btn btn-default btn-block" ng-show="vm.show" ng-click="vm.show = false">Hide Alert</a>
        </div>
        <div class="col-sm-8">
          <xos-alert config="vm.config1" show="vm.show">
            A sample alert message, not displayed by default.
          </xos-alert>
        </div>
      </div>
    </file>
    <file name="script.js">
      angular.module('sampleAlert2', ['xos.uiComponents', 'ngAnimate'])
      .controller('SampleCtrl', function(){
        this.config1 = {
          type: 'success'
        };

        this.show = false;
      });
    </file>
  </example>
  **/

  .directive('xosAlert', function(){
    return {
      restrict: 'E',
      scope: {
        config: '=',
        show: '=?'
      },
      template: `
        <div ng-cloak class="alert alert-{{vm.config.type}}" ng-hide="!vm.show">
          <button type="button" class="close" ng-if="vm.config.closeBtn" ng-click="vm.dismiss()">
            <span aria-hidden="true">&times;</span>
          </button>
          <p ng-transclude></p>
        </div>
      `,
      transclude: true,
      bindToController: true,
      controllerAs: 'vm',
      controller: function($timeout){

        if(!this.config){
          throw new Error('[xosAlert] Please provide a configuration via the "config" attribute');
        }

        // default the value to true
        this.show = this.show !== false;
        
        this.dismiss = () => {
          this.show = false;
        }

        if(this.config.autoHide){
          let to = $timeout(() => {
            this.dismiss();
            $timeout.cancel(to);
          }, this.config.autoHide);
        }
      }
    }
  })
})();
