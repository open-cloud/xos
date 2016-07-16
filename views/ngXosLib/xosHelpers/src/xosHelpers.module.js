(function() {
  'use strict';

  /**
  * @ngdoc overview
  * @name xos.helpers
  * @description
  * # xos.Helpers
  * A collection of helpers to work with XOS <br/>
  * Currently available components are:
  * - [NoHyperlinks](/#/module/xos.helpers.NoHyperlinks)
  * - [SetCSRFToken](/#/module/xos.helpers.SetCSRFToken)
  * - [xosNotification](/#/module/xos.helpers.xosNotification)
  * - [XosUserPrefs](/#/module/xos.helpers.XosUserPrefs)
  * <br/><br/>
  * A set of angular [$resource](https://docs.angularjs.org/api/ngResource/service/$resource) is provided to work with the API.<br>
  * You can find the documentation [here](#/rest-api)
  **/

  angular
      .module('xos.helpers', [
        'ngCookies',
        'ngResource',
        'ngAnimate',
        'xos.uiComponents'
      ])
      .config(config)

      /**
      * @ngdoc service
      * @name xos.helpers._
      * @description Wrap [lodash](https://lodash.com/docs) in an Angular Service
      **/

      .factory('_', $window => $window._ );

  function config($httpProvider, $interpolateProvider, $resourceProvider) {
    $httpProvider.interceptors.push('SetCSRFToken');

    $interpolateProvider.startSymbol('{$');
    $interpolateProvider.endSymbol('$}');

    // NOTE http://www.masnun.com/2013/09/18/django-rest-framework-angularjs-resource-trailing-slash-problem.html
    $resourceProvider.defaults.stripTrailingSlashes = false;
  }
})();