(function () {
  'use strict';
  angular.module('xos.UITutorial')
  .service('ResponseHandler', function(){
    this.parse = (res, done) => {
      // TODO @Arpit format res (it can be an array or an object),
      // it is better if the output is a valid JSON (that we can copy and paste)
      // TODO handle 204/No-Content response
      if(angular.isArray(res)){
        res = res.map(i => {
          return JSON.stringify(i, ['id', 'name', 'max_instances'], 2) + '<br/>';
        });
      }
      else {
        res = JSON.stringify(res, ['id', 'name', 'max_instances'], 2);
      }

      done(res);
    };
  });
})();