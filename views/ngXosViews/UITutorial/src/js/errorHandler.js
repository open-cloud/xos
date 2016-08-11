(function () {
  'use strict';
  angular.module('xos.UITutorial')
  .service('ErrorHandler', function(TemplateHandler){
    this.print = (msg, done) => {
      done(TemplateHandler.error({msg: msg}));
    };
  });
})();