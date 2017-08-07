
/*
 * Copyright 2017-present Open Networking Foundation

 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at

 * http://www.apache.org/licenses/LICENSE-2.0

 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */


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