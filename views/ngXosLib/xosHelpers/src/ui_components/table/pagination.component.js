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
  .directive('xosPagination', function(){
    return {
      restrict: 'E',
      scope: {
        pageSize: '=',
        totalElements: '=',
        change: '='
      },
      template: `
        <div class="row">
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
            this.pages = Math.round(this.totalElements / this.pageSize);
            this.pageList = this.createPages(this.pages);
          }
          // scope.getPages();
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
