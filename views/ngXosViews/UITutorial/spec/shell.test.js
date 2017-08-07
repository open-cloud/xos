
/*
 * Copyright 2017-present Open Networking Foundation

 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at

 * http://www.apache.org/licenses/LICENSE-2.0

 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */


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