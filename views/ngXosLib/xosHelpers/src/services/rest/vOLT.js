'use strict';

/*
 * OLT devices aggregate a set of subscriber connections

 */

angular.module('xos.helpers')
.service('vOLT-Collection', function($resource){
  return $resource('/api/tenant/cord/volt/:volt_id/', { volt_id: '@id'});
})
