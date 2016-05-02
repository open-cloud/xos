(function() {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Login
  * @description Angular resource to fetch /api/utility/login/
  **/
  .service('Login', function($resource){
    return $resource('/api/utility/login/');
  })
  /**
  * @ngdoc service
  * @name xos.helpers.Logout
  * @description Angular resource to fetch /api/utility/logout/
  **/
  .service('Logout', function($resource){
    return $resource('/api/utility/logout/');
  })
})();