'use strict';

describe('The Js Shell directive', () => {
  
  var scope, element, isolatedScope, shellSpy;

  beforeEach(module('xos.UITutorial'));
  beforeEach(module('templates'));

  beforeEach(inject(function($compile, $rootScope){
    scope = $rootScope.$new();
    element = angular.element('<js-shell></js-shell>');
    $compile(element)(scope);
    scope.$digest();
    isolatedScope = element.isolateScope().vm;
    spyOn(isolatedScope.shell, 'setCommandHandler');
    spyOn(isolatedScope.shell, 'activate');
  }));

  // NOTE see http://stackoverflow.com/questions/38906605/angular-jasmine-testing-immediatly-invoked-functions-inside-a-directive-contr

  xit('should register the explore command', () => {
    expect(isolatedScope.shell.setCommandHandler).toHaveBeenCalled();
  });

  xit('should activate the shell', () => {
    expect(isolatedScope.shell.activate).toHaveBeenCalled();
  });
});