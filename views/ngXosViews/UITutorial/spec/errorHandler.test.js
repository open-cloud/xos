'use strict';

describe('The ErrorHandler service', () => {
  
  var ErrorHandler, done;

  beforeEach(module('xos.UITutorial'));
  beforeEach(module('templates'));

  beforeEach(inject(function (_ErrorHandler_) {
    // The injector unwraps the underscores (_) from around the parameter names when matching
    ErrorHandler = _ErrorHandler_;
    done = jasmine.createSpy('done');
  }));

  describe('the print method', () => {
    it('should return an html template', () => {
      ErrorHandler.print('myError', done);
      expect(done).toHaveBeenCalledWith(`<span class="error">[ERROR] myError</span>`)
    });
  });
});