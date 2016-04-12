'use strict';

/*
 * List of the active onos services

 */

angular.module('xos.helpers')
.service('ONOS-Services-Collection', function($resource){
  return $resource('/api/service/onos/');
})
