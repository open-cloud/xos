'use strict';

angular.module('xos.UITutorial', [
  'ngResource',
  'ngCookies',
  'ui.router',
  'xos.helpers',
  'ui.ace'
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
.directive('jsShell', function($rootScope, TemplateHandler, codeToString){
  return {
    restrict: 'E',
    scope: {},
    bindToController: true,
    controllerAs: 'vm',
    templateUrl: 'templates/js-shell.tpl.html',
    controller: function(ExploreCmd, PlayCmd, LearnCmd){
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

      this.shell.setCommandHandler('learn', {
        exec: (cmd, args, done) => {
          LearnCmd.setup(this.shell);
          done(TemplateHandler.instructions({
            title: `You can now learn the API`,
            messages: [
              `Use <code>next</code> to move to the next lesson <code>resource {resoureName} {method} {?paramters}</code> to call the API.`,
              `An example command is <code>resource Slices query</code>`,
              `You can also provide paramters with <code>next</code>`
            ]
          }));
        }
      });
      
      this.shell.setCommandHandler('play', {
        exec: (cmd, args, done) => {
          PlayCmd.setup(this.shell);
          done(TemplateHandler.instructions({
            title: `You can now play with UI components!`,
            messages: [
              `Use <code>component list</code> to list all the available component and <code>component {componentName}</code> to startusing it.`,
              `An example command is <code>component xosTable</code>`
            ]
          }));
        }
      });

      this.shell.activate();

      this.componentScope = null;

      $rootScope.$on('uiTutorial.attachScope', (e, scope) => {
        this.componentScope = {
          config: JSON.stringify(codeToString.toString(scope.config), null, 2),
          data: JSON.stringify(codeToString.toString(scope.data), null, 2)
        };
      });

      this.applyScope = (scope) => {
        
        // let a = codeToString.toCode(scope.config);
        // console.log(a);
        const newScope = {
          config: codeToString.toCode(scope.config),
          data: eval(`(${scope.data})`)
        };

        $rootScope.$emit('uiTutorial.applyScope', newScope);
      }

    }
  };
});