(function() {
    'use strict';
    console.log('XOS Helpers Module')
    angular.module('bugSnag', []).factory('$exceptionHandler', function () {
      return function (exception, cause) {
        if( window.Bugsnag ){
          Bugsnag.notifyException(exception, {diagnostics:{cause: cause}});
        }
        else{
          console.error(exception, cause, exception.stack);
        }
      };
    });

    angular
        .module('xos.helpers',[
          'ngCookies',
          'ngResource',
          'xos.xos',
          'xos.hpcapi',
          'xos.xoslib',
          'bugSnag',
          'xos.uiComponents'
        ])
        .config(config);

    function config($httpProvider, $interpolateProvider, $resourceProvider) {
      $httpProvider.interceptors.push('SetCSRFToken');

      $interpolateProvider.startSymbol('{$');
      $interpolateProvider.endSymbol('$}');

      // NOTE http://www.masnun.com/2013/09/18/django-rest-framework-angularjs-resource-trailing-slash-problem.html
      $resourceProvider.defaults.stripTrailingSlashes = false;
    }
})();