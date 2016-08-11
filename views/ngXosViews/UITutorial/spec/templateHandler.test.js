'use strict';

describe('The TemplateHandler service', () => {
  
  var TemplateHandler;

  beforeEach(module('xos.UITutorial'));
  beforeEach(module('templates'));

  beforeEach(inject(function (_TemplateHandler_) {
    TemplateHandler = _TemplateHandler_;
  }));

  const templates = ['error', 'instructions', 'resourcesResponse'];

  templates.forEach(t => {
    it(`should have a ${t} template`, () => {
      expect(TemplateHandler[t]).toBeDefined();
      expect(angular.isFunction(TemplateHandler[t])).toBeTruthy();
    });
  });
});