(function () {
  'use strict';
  angular.module('xos.UITutorial')
  .service('ErrorHandler', function(){
    this.print = (msg, done) => {
      const errorTpl = _.template(`<span class="error">[ERROR] <%= msg %></span>`);
      done(errorTpl({msg: msg}));
    };
  });
})();