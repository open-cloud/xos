(function() {
  'use strict';

    angular
        .module('xos.helpers')
        .service('XosApi', xosApi)
        .service('XoslibApi', xoslibApi)
        .service('HpcApi', hpcApi);

    var xosApiCache, xoslibApiCache, hpcApiCache;

    function xosApi(xos) { 
      if(!xosApiCache){
        xosApiCache = new xos({domain: ''});
      }
      return xosApiCache;
    }

    function xoslibApi(xoslib) { 
      if(!xoslibApiCache){
        xoslibApiCache = new xoslib({domain: ''});
      }
      return xoslibApiCache;
    }

    function hpcApi(hpcapi) { 
      if(!hpcApiCache){
        hpcApiCache = new hpcapi({domain: ''});
      }
      return hpcApiCache;
    }
})();
