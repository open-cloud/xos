
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

describe('The ExploreCmd service', () => {
  
  var ExploreCmd, ErrorHandler, ResponseHandler, done, shell, ResourceMock, rootScope;

  beforeEach(module('xos.UITutorial'));
  beforeEach(module('templates'));

  beforeEach(() => {
    module(function ($provide) {
      $provide.value('Resource', ResourceMock);
    })
  });

  beforeEach(inject(function (_ExploreCmd_, _ErrorHandler_, _ResponseHandler_, $rootScope) {
    // The injector unwraps the underscores (_) from around the parameter names when matching
    ExploreCmd = _ExploreCmd_;
    ErrorHandler = _ErrorHandler_;
    ResponseHandler = _ResponseHandler_;
    rootScope = $rootScope;
    done = jasmine.createSpy('done');
    shell = {
      setCommandHandler: jasmine.createSpy('setCommandHandler'),
      bestMatch: jasmine.createSpy('bestMatch')
    };
    // binding the mock shell to the service (for easy testing)
    ExploreCmd.shell = shell;
    spyOn(console, 'error');

    ResourceMock = {
      query: jasmine.createSpy('query').and.callFake(() => {
        var deferred = $q.defer();
        deferred.resolve('Remote call result');
        return {$promise: deferred.promise};
      })
    };
  }));

  it('should set the resouce command handler', () => {
    ExploreCmd.setup(shell);
    expect(shell.setCommandHandler).toHaveBeenCalledWith('resource', { exec: ExploreCmd.resourceExec, completion: ExploreCmd.resourceCompletion })
  });

  describe('the resourceCompletion function', () => {

    beforeEach(() => {
      spyOn(ExploreCmd, 'getAvailableResources').and.returnValue(['Sites', 'Slices']);
    });

    it('should suggest a resource list', () => {
      ExploreCmd.resourceCompletion('resource', '', {text: 'resource'}, done)
      expect(shell.bestMatch).toHaveBeenCalledWith('', [ 'list', 'Sites', 'Slices' ]);

      ExploreCmd.resourceCompletion('resource', 'S', {text: 'resource S'}, done)
      expect(shell.bestMatch).toHaveBeenCalledWith('S', [ 'list', 'Sites', 'Slices' ]);
    });

    it('should suggest a method list', () => {
      ExploreCmd.resourceCompletion('resource', '', {text: 'resource Sites '}, done)
      expect(shell.bestMatch).toHaveBeenCalledWith('', [ 'query', 'get', 'save', '$save', 'delete' ]);

      ExploreCmd.resourceCompletion('resource', 'q', {text: 'resource Sites q'}, done)
      expect(shell.bestMatch).toHaveBeenCalledWith('q', [ 'query', 'get', 'save', '$save', 'delete' ]);
    });
  });

  describe('the resourceExec function', () => {

    beforeEach(() => {
      spyOn(ExploreCmd, 'listAvailableResources');
      spyOn(ExploreCmd, 'consumeResource');
    });

    it('should list available resources', () => {
      ExploreCmd.resourceExec('explore', ['list'], done);
      expect(ExploreCmd.listAvailableResources).toHaveBeenCalledWith(done);
    });

    it('should use a resource', () => {
      ExploreCmd.resourceExec('explore', ['Resource', 'query'], done);
      expect(ExploreCmd.consumeResource).toHaveBeenCalledWith('Resource', 'query', [], done);
    });
  });

  describe('the getAvailableResources function', () => {

    beforeEach(() => {
      spyOn(angular, 'module').and.returnValue({
        _invokeQueue: [
          ['$provide', 'service', ['Sites', ['$resource']]],
          ['$provide', 'service', ['Slices', ['$q', '$resource']]],
          ['$provide', 'factory', ['_', []]],
          ['$provide', 'service', ['helper', ['Slices']]]
        ]
      });
    });

    it('should return a list of resources in the angular app', () => {
      const resources = ExploreCmd.getAvailableResources();
      expect(resources).toEqual(['Sites', 'Slices']);
    });
  });

  describe('the listAvailableResources function', () => {
    beforeEach(() => {
      spyOn(ExploreCmd, 'getAvailableResources').and.returnValue(['Sites', 'Slices']);
    });

    it('should format resource in an html template', () => {
      ExploreCmd.listAvailableResources(done);
      expect(ExploreCmd.getAvailableResources).toHaveBeenCalled();
      expect(done).toHaveBeenCalledWith(`Sites<br/>Slices<br/>`);
    });
  });

  describe('the consumeResource function', () => {
    beforeEach(() => {
      spyOn(ExploreCmd, 'getAvailableResources').and.returnValue(['Resource', 'Fake']);
      spyOn(ErrorHandler, 'print');
    });

    it('should notify that a resource does not exists', () => {
      ExploreCmd.consumeResource('Test', null, null, done);
      expect(ErrorHandler.print).toHaveBeenCalledWith(`Resource "Test" does not exists`, done)
    });

    it('should notify that a method does not exists', () => {
      ExploreCmd.consumeResource('Resource', 'test', null, done);
      expect(ErrorHandler.print).toHaveBeenCalledWith(`Method "test" not allowed`, done)
    });

    const methodsWithParams = ['get', '$save', 'delete'];
    methodsWithParams.forEach(method => {
      it(`should notify that the ${method} method require parameters`, () => {
        ExploreCmd.consumeResource('Resource', method, [], done);
        expect(ErrorHandler.print).toHaveBeenCalledWith(`Method "${method}" require parameters`, done)
      });
    });

    it('should not accept id as parameter for the query method', () => {
      ExploreCmd.consumeResource('Resource', 'query', ['{id:1}'], done);
      expect(ErrorHandler.print).toHaveBeenCalledWith(`Is not possible to use "id" as filter in method "query", use "get" instead!`, done)
    });

    it('should notify the user in case of malformed parameters', () => {
      ExploreCmd.consumeResource('Resource', 'query', ['{child: 3}'], done);
      expect(ErrorHandler.print).toHaveBeenCalledWith(`Parameter is not valid, it shoudl be in the form of: <code>{id:1}</code>, with no spaces`, done)
      pending();
    });

    describe('when called with the correct parameters', () => {

      let deferred;
      beforeEach(inject(($q) => {
        spyOn(ResponseHandler, 'parse');

        deferred = $q.defer();
        ResourceMock = {
          query: jasmine.createSpy('query').and.callFake(function(){
            return {$promise: deferred.promise};
          })
        };
      }));

      it('should notify the user if an error occurred while loading the resource', () => {
        ExploreCmd.consumeResource('Fake', 'query', [], done);
        expect(console.error).toHaveBeenCalled();
        expect(ErrorHandler.print).toHaveBeenCalledWith('Failed to inject resource "Fake"', done);
      });

      it('should call a resource and return the results', () => {
        ExploreCmd.consumeResource('Resource', 'query', [], done);
        deferred.resolve([]);
        rootScope.$apply();
        expect(ErrorHandler.print).not.toHaveBeenCalled()
        expect(ResponseHandler.parse).toHaveBeenCalledWith([], 'Resource.query()', done);
      });

      it('should call a resource with parameters and return the results', () => {
        ExploreCmd.consumeResource('Resource', 'query', ['{child:3}'], done);
        deferred.resolve([]);
        rootScope.$apply();
        expect(ErrorHandler.print).not.toHaveBeenCalled()
        expect(ResponseHandler.parse).toHaveBeenCalledWith([], 'Resource.query({"child":3})', done);
      });

      it('should call a resource and display a not found message', () => {
        ExploreCmd.consumeResource('Resource', 'query', [], done);
        deferred.reject({status: 404, data: {detail: 'Not Found.'}});
        rootScope.$apply();
        expect(ErrorHandler.print).toHaveBeenCalledWith('Resource with method "query" and parameters {} Not Found.', done)
        expect(ResponseHandler.parse).not.toHaveBeenCalled();
      });
    });
  });
});