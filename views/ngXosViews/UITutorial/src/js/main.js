'use strict';

angular.module('xos.UITutorial', [
  'ngResource',
  'ngCookies',
  'ui.router',
  'xos.helpers'
])
.config(($stateProvider) => {
  $stateProvider
  .state('shell', {
    url: '/',
    template: '<js-shell></js-shell>'
  });
})
.config(function($httpProvider){
  $httpProvider.interceptors.push('NoHyperlinks');
})
.directive('jsShell', function(){
  return {
    restrict: 'E',
    scope: {},
    bindToController: true,
    controllerAs: 'vm',
    templateUrl: 'templates/js-shell.tpl.html',
    controller: function(ExploreCmd){
      var history = new Josh.History({ key: 'helloworld.history'});
      var shell = Josh.Shell({history: history});

      shell.onNewPrompt(function(done) {
        done('[ngXosLib] $ ');
      });

      shell.setCommandHandler('explore', {
        exec: (cmd, args, done) => {
          ExploreCmd.setup(shell);
          done();
        }
      });



      shell.activate();
    }
  };
});