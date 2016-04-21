(function() {
  'use strict';

  /**
  * @ngdoc service
  * @name xos.helpers.SetCSRFToken
  * @description This factory is automatically loaded trough xos.helpers and will add an $http interceptor that will the CSRF-Token to your request headers
  **/

  angular
      .module('xos.helpers')
      .factory('SetCSRFToken', setCSRFToken);

  function setCSRFToken($cookies) {
    return {
      request: function(request){
        if(request.method !== 'GET'){
          request.headers['X-CSRFToken'] = $cookies.get('xoscsrftoken');
        }
        return request;
      }
    };
  }
})();
