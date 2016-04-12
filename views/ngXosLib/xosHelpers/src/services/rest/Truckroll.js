'use strict';

/*
 * Virtual Truckroll, enable to perform basic test on user connectivity such as ping, traceroute and tcpdump.

 */

angular.module('xos.helpers')
.service('Truckroll-Collection', function($resource){
  return $resource('/api/tenant/truckroll/:truckroll_id/', { truckroll_id: '@id' });
})
