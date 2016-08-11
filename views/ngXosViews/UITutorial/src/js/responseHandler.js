(function () {
  'use strict';
  angular.module('xos.UITutorial')
  .service('ResponseHandler', function(){
    this.parse = (res, done) => {
      var compiled = _.template('<div><pre><%- JSON.stringify(val,null,1) %></div></pre>');
      var compiledArray = _.template('<% _.forEach(valueArr, function(item) { %><div><pre><%- JSON.stringify(item) %></pre></div><%}); %>');
      var resFunc = function (res) {
        let retVar;
        let exclude = ['deleted','enabled','enacted','exposed_ports','lazy_blocked','created','validators','controllers','backend_status','backend_register','policed','no_policy','write_protect','no_sync','updated'];
        if(_.isArray(res)) {
          retVar = [];
          retVar = _.map(res, (o)=> {
            return _.omit(o, exclude);
          });
          retVar = compiledArray({'valueArr':retVar});
        }
        else{
          retVar = _.omit(res,exclude);
          retVar = compiled({'val':retVar} );
        }
        return retVar;
      }
      done( resFunc(res));
    };
  });
})();