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
.directive('jsShell', function(TemplateHandler){
  return {
    restrict: 'E',
    scope: {},
    bindToController: true,
    controllerAs: 'vm',
    templateUrl: 'templates/js-shell.tpl.html',
    controller: function(ExploreCmd){
      var history = new Josh.History({ key: 'jsshell.history'});
      this.shell = Josh.Shell({history: history});

      this.shell.onNewPrompt(done => {
        done('[ngXosLib] $ ');
      });

      this.shell.setCommandHandler('explore', {
        exec: (cmd, args, done) => {
          ExploreCmd.setup(this.shell);
          done(TemplateHandler.instructions({
            title: `You can now explore the API use angular $resouces!`,
            messages: [
              `Use <code>resource list</code> to list all the available resources and <code>resource {resoureName} {method} {?paramters}</code> to call the API.`,
              `An example command is <code>resource Slices query</code>`,
              `You can also provide paramters with <code>resource Slices query {max_instances: 10}</code>`
            ]
          }));
        }
      });

      this.shell.activate();
    }
  };
});