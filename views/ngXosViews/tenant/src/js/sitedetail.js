/**
 * Created by arpit on 7/7/2016.
 */
'use strict';

angular.module('xos.tenant')
.directive('siteDetail', function(){
  return {
    restrict: 'E',
    scope: {},
    bindToController: true,
    controllerAs: 'sl',
    templateUrl: 'templates/slicelist.html',
    controller: function(SlicesPlus, $stateParams){
      this.siteId  = $stateParams.id;
      this.tableConfig = {
        columns: [
          {
            label: 'Slice List',
            prop: 'name',
            link: item => `#/site/${item.site}/slice/${item.id}`
          },
          {
            label: 'Allocated',
            prop: 'instance_total'
          },
          {
            label: 'Ready',
            prop: 'instance_total_ready'
          }
        ]
      };

      // retrieving user list
      SlicesPlus.query({
        site: $stateParams.id
      }).$promise
      .then((users) => {
        this.sliceList = users;
      })
      .catch((e) => {
        throw new Error(e);
      });
    }
  };
});