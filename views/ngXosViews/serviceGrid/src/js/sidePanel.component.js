/**
 * © OpenCORD
 *
 * Visit http://guide.xosproject.org/devguide/addview/ for more information
 *
 * Created by teone on 7/18/16.
 */

(function () {
  'use strict';

  angular.module('xos.uiComponents')
  .directive('xosSidePanel', function(){
    return {
      restrict: 'E',
      scope: {
        config: '=',
        show: '='
      },
      template: `
        <div class="xos-side-panel-content {{vm.classes.join(' ')}}">
          <div class="row">
            <div class="col-xs-12">
              <button type="button" class="close" ng-click="vm.dismiss()">
                <span aria-hidden="true">&times;</span>
              </button>
            </div>
          </div>
          <div class="row">
            <div class="col-xs-12" ng-transclude></div>
          </div>
        </div>
      `,
      transclude: true,
      bindToController: true,
      controllerAs: 'vm',
      controller: function($scope, $timeout, _){
        console.log(this.show);

        this.classes = [];

        this.classes.push(this.config.position);

        this.dismiss = () => {
          this.show = false;
          this.classes = this.toggleClass(this.classes);
          $timeout(() => {
            return _.remove(this.classes, c => c === 'out');
          }, 500);
        };

        this.toggleClass = (classes) => {
          if(classes.indexOf('in') > -1){
            _.remove(this.classes, c => c === 'in');
            this.classes.push('out');
            return classes;
          }
          _.remove(this.classes, c => c === 'out');
          this.classes.push('in');
          return classes;
        };

        $scope.$watch(() => this.show, val => {
          if (angular.isDefined(val)){
            if (val && val === true){
              this.classes = this.toggleClass(this.classes);
            }
          }
        })
      }
    }
  });
})();

