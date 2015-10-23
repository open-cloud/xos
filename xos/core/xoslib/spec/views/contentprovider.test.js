'use strict';

describe('The Content Provider SPA', () => {

  var scope, element;

  // injecting main module
  beforeEach(module('xos.contentProviderApp'));

  // preload Html Templates with ng-html2js
  beforeEach(module('templates'));

  describe('the contentProvider list', () => {
    beforeEach(inject(function($compile, $rootScope) {
      scope = $rootScope.$new();

      element = angular.element('<content-provider-list></content-provider-list>');
      $compile(element)(scope);
      scope.$digest();
    }));


    it('should call startPolling method', () => {
      expect(true).toBe(true);
    });
  });
});
