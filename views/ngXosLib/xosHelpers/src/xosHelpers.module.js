(function() {
    'use strict';

    angular
        .module('xos.helpers',[
          'ngCookies',
          'xos.xos',
          'xos.hpcapi',
          'xos.xoslib'
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