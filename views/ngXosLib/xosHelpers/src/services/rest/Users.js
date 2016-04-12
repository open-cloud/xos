'use strict';

/*
 * List of the XOS users

 */

angular.module('xos.helpers')
.service('Users', function($resource){
  return $resource('/api/core/users/');
})
