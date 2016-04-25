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
    * @name xos.uiComponents.directive:xosPagination
    * @restrict E
    * @description The xos-table directive
    * @param {Number} pageSize Number of elements per page
    * @param {Number} totalElements Number of total elements in the collection
    * @param {Function} change The callback to be triggered on page change.
    * * @element ANY
    * @scope
    * @example
  <example module="samplePagination">
    <file name="index.html">
      <div ng-controller="SampleCtrl1 as vm">
        <xos-pagination
          page-size="vm.pageSize"
          total-elements="vm.totalElements"
          change="vm.change">
        </xos-pagination>
      </div>
    </file>
    <file name="script.js">
      angular.module('samplePagination', ['xos.uiComponents'])
      .controller('SampleCtrl1', function(){
        this.pageSize = 10;
        this.totalElements = 35;
        this.change = (pageNumber) => {
          console.log(pageNumber);
        }
      });
    </file>
  </example>
  **/

  .directive('xosPagination', function(){
    return {
      restrict: 'E',
      scope: {
        pageSize: '=',
        totalElements: '=',
        change: '='
      },
      template: `
        <div class="row" ng-if="vm.pageList.length > 1">
          <div class="col-xs-12 text-center">
            <ul class="pagination">
              <li
                ng-click="vm.goToPage(vm.currentPage - 1)"
                ng-class="{disabled: vm.currentPage == 0}">
                <a href="" aria-label="Previous">
                    <span aria-hidden="true">&laquo;</span>
                </a>
              </li>
              <li ng-repeat="i in vm.pageList" ng-class="{active: i === vm.currentPage}">
                <a href="" ng-click="vm.goToPage(i)">{{i + 1}}</a>
              </li>
              <li
                ng-click="vm.goToPage(vm.currentPage + 1)"
                ng-class="{disabled: vm.currentPage == vm.pages - 1}">
                <a href="" aria-label="Next">
                    <span aria-hidden="true">&raquo;</span>
                </a>
              </li>
            </ul>
          </div>
        </div>
      `,
      bindToController: true,
      controllerAs: 'vm',
      controller: function($scope){
        
        this.currentPage = 0;

        this.goToPage = (n) => {
          if(n < 0 || n === this.pages){
            return;
          }
          this.currentPage = n;
          this.change(n);
        }

        this.createPages = (pages) => {
          let arr = [];
          for(var i = 0; i < pages; i++){
            arr.push(i);
          }
          return arr;
        }

        // watch for data changes
        $scope.$watch(() => this.totalElements, () => {
          if(this.totalElements){
            this.pages = Math.ceil(this.totalElements / this.pageSize);
            this.pageList = this.createPages(this.pages);
          }
        });
      }
    }
  })
  .filter('pagination', function(){
    return function(input, start) {
      if(!input || !angular.isArray(input)){
        return input;
      }
      start = parseInt(start, 10);
      return input.slice(start);
    };
  });
})();
