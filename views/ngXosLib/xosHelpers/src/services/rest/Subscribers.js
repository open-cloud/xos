(function() {
  'use strict';

  angular.module('xos.helpers')
  /**
  * @ngdoc service
  * @name xos.helpers.Subscribers
  * @description Angular resource to fetch Subscribers
  **/
  .service('Subscribers', function($resource){
    return $resource('/api/tenant/cord/subscriber/:id/', { id: '@id' }, {
      update: { method: 'PUT' },
      /**
      * @ngdoc method
      * @name xos.helpers.Subscribers#View-a-Subscriber-Features-Detail
      * @methodOf xos.helpers.Subscribers
      * @description
      * View-a-Subscriber-Features-Detail
      **/
      'View-a-Subscriber-Features-Detail': {
        method: 'GET',
        isArray: false,
        url: '/api/tenant/cord/subscriber/:id/features/'
      },
      /**
      * @ngdoc method
      * @name xos.helpers.Subscribers#Read-Subscriber-uplink_speed
      * @methodOf xos.helpers.Subscribers
      * @description
      * Read-Subscriber-uplink_speed
      **/
      'Read-Subscriber-uplink_speed': {
        method: 'GET',
        isArray: false,
        url: '/api/tenant/cord/subscriber/:id/features/uplink_speed/'
      },
      /**
      * @ngdoc method
      * @name xos.helpers.Subscribers#Update-Subscriber-uplink_speed
      * @methodOf xos.helpers.Subscribers
      * @description
      * Update-Subscriber-uplink_speed
      **/
      'Update-Subscriber-uplink_speed': {
        method: 'PUT',
        isArray: false,
        url: '/api/tenant/cord/subscriber/:id/features/uplink_speed/'
      },
      /**
      * @ngdoc method
      * @name xos.helpers.Subscribers#Read-Subscriber-downlink_speed
      * @methodOf xos.helpers.Subscribers
      * @description
      * Read-Subscriber-downlink_speed
      **/
      'Read-Subscriber-downlink_speed': {
        method: 'GET',
        isArray: false,
        url: '/api/tenant/cord/subscriber/:id/features/downlink_speed/'
      },
      /**
      * @ngdoc method
      * @name xos.helpers.Subscribers#Update-Subscriber-downlink_speed
      * @methodOf xos.helpers.Subscribers
      * @description
      * Update-Subscriber-downlink_speed
      **/
      'Update-Subscriber-downlink_speed': {
        method: 'PUT',
        isArray: false,
        url: '/api/tenant/cord/subscriber/:id/features/downlink_speed/'
      },
      /**
      * @ngdoc method
      * @name xos.helpers.Subscribers#Read-Subscriber-cdn
      * @methodOf xos.helpers.Subscribers
      * @description
      * Read-Subscriber-cdn
      **/
      'Read-Subscriber-cdn': {
        method: 'GET',
        isArray: false,
        url: '/api/tenant/cord/subscriber/:id/features/cdn/'
      },
      /**
      * @ngdoc method
      * @name xos.helpers.Subscribers#Update-Subscriber-cdn
      * @methodOf xos.helpers.Subscribers
      * @description
      * Update-Subscriber-cdn
      **/
      'Update-Subscriber-cdn': {
        method: 'PUT',
        isArray: false,
        url: '/api/tenant/cord/subscriber/:id/features/cdn/'
      },
      /**
      * @ngdoc method
      * @name xos.helpers.Subscribers#Read-Subscriber-uverse
      * @methodOf xos.helpers.Subscribers
      * @description
      * Read-Subscriber-uverse
      **/
      'Read-Subscriber-uverse': {
        method: 'GET',
        isArray: false,
        url: '/api/tenant/cord/subscriber/:id/features/uverse/'
      },
      /**
      * @ngdoc method
      * @name xos.helpers.Subscribers#Update-Subscriber-uverse
      * @methodOf xos.helpers.Subscribers
      * @description
      * Update-Subscriber-uverse
      **/
      'Update-Subscriber-uverse': {
        method: 'PUT',
        isArray: false,
        url: '/api/tenant/cord/subscriber/:id/features/uverse/'
      },
      /**
      * @ngdoc method
      * @name xos.helpers.Subscribers#Read-Subscriber-status
      * @methodOf xos.helpers.Subscribers
      * @description
      * Read-Subscriber-status
      **/
      'Read-Subscriber-status': {
        method: 'GET',
        isArray: false,
        url: '/api/tenant/cord/subscriber/:id/features/status/'
      },
      /**
      * @ngdoc method
      * @name xos.helpers.Subscribers#Update-Subscriber-status
      * @methodOf xos.helpers.Subscribers
      * @description
      * Update-Subscriber-status
      **/
      'Update-Subscriber-status': {
        method: 'PUT',
        isArray: false,
        url: '/api/tenant/cord/subscriber/:id/features/status/'
      }
    })
  })
})();