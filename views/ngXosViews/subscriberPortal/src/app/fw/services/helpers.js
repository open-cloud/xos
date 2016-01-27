(function () {
  "use strict";

  angular.module('cordGui')
  .service('Helpers', function(){
    this.randomDate = function(start, end) {
      return new Date(
        start.getTime() + Math.random() * (end.getTime() - start.getTime())
      );
    }
  });

}());