/**
 * © OpenCORD
 *
 * Visit http://guide.xosproject.org/devguide/addview/ for more information
 *
 * Created by teone on 6/27/16.
 */

(function () {
  'use strict';

  angular.module('xos.ecordTopology')
    .service('Uni', ($resource, _) => {
      return $resource(`/api/service/metronetworkservice/SCA_ETH_FPP_UNI_N/:id`, {id: '@id'}, {
        query: {
          isArray: true,
          interceptor: {
            response: (res) => {
              const augmentedUnis = _.map(res.data, (uni, i) => {
                var latlng_val = uni.latlng;
                var lat_val = latlng_val.substring(1, latlng_val.indexOf(',') - 1);
                lat_val = lat_val.trim();
                var lng_val = latlng_val.substring(latlng_val.indexOf(',') + 1, latlng_val.length - 1);
                lng_val = lng_val.trim()

                uni.latlng = [lat_val, lng_val];
                return uni;
              });
              return augmentedUnis;
            }
          }
        }
      });
    });
})();

